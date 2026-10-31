"""Real CPU inference; candidate-restriction diagnostics and matched cascade traces."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[key]='1'
os.environ['TOKENIZERS_PARALLELISM']='false'
import argparse,gzip,hashlib,json,pickle,time,platform
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import transformers
from transformers import AutoTokenizer,AutoModelForSequenceClassification
from lazy_cert_study.core import screen,IncrementalScorer,topk
from lazy_cert_study.benchmark import View

ROOT=Path(__file__).resolve().parent


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def rank_scores(scores,documents,product_ids):
    documents=np.asarray(documents,dtype=int)
    return documents[np.lexsort((np.asarray(product_ids)[documents],-np.asarray(scores)))].tolist()


def qrel_metric(top,grades,ids):
    rel=[grades.get(ids[int(d)],0) for d in top[:10]]
    ideal=sorted(grades.values(),reverse=True)[:10]
    dcg=sum((2**r-1)/np.log2(i+2) for i,r in enumerate(rel))
    idcg=sum((2**r-1)/np.log2(i+2) for i,r in enumerate(ideal))
    return {'nDCG10':float(dcg/idcg) if idcg else 0.,'hasPositiveQrel':bool(idcg),
            'judgedTop10':sum(ids[int(d)] in grades for d in top[:10]),
            'positiveTop10':sum(r>=1 for r in rel)}


class Predictor:
    def __init__(self,path,texts):
        self.texts=texts;self.tokenizer=AutoTokenizer.from_pretrained(path,local_files_only=True)
        self.model=AutoModelForSequenceClassification.from_pretrained(path,local_files_only=True,attn_implementation='sdpa').eval()
        torch.set_num_threads(4);torch.set_num_interop_threads(1)
        self.calls=0
    def score(self,query,documents):
        start=time.perf_counter();result=[];at_limit=0
        with torch.inference_mode():
            for offset in range(0,len(documents),32):
                ds=documents[offset:offset+32]
                batch=self.tokenizer([query]*len(ds),[self.texts[int(d)] for d in ds],
                                     padding='max_length',truncation=True,max_length=256,return_tensors='pt')
                at_limit+=int((batch['attention_mask'].sum(1)==256).sum())
                result.extend(self.model(**batch).logits[:,0].cpu().tolist());self.calls+=1
        return np.asarray(result),{'seconds':time.perf_counter()-start,'pairs':len(documents),
                                   'atTokenLimit':at_limit,'tokenLimitCountIsUpperBoundOnTruncated':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    spec=json.loads((ROOT/'MODEL_SOURCE.json').read_text())
    for f in spec['files']:assert digest(a.model/f['name'])==f['sha256']
    src=json.loads((ROOT.parent/'lazy_cert_study/sources.json').read_text())
    for f in src['files']:assert digest(a.data/f['path'])==f['sha256']
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:old=[json.loads(s) for s in f]
    assert all(r['modelHash']==index.model_hash for r in old)
    queries=pd.read_csv(a.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('');qtext=dict(zip(queries.query_id,queries['query']))
    products=pd.read_csv(a.data/'dataset/product.csv',sep='\t',dtype={'product_id':str}).fillna('')
    product_text={str(r['product_id']):' '.join(str(r[k]) for k in ['product_name','product_class','product_description']) for r in products.to_dict('records')}
    texts=[product_text[i] for i in index.ids]
    labels=pd.read_csv(a.data/'dataset/label.csv',sep='\t',dtype={'query_id':str,'product_id':str})
    grade_map={'Exact':2,'Partial':1,'Irrelevant':0};gold={}
    for r in labels.to_dict('records'):
        d=gold.setdefault(r['query_id'],{});d[r['product_id']]=max(d.get(r['product_id'],0),grade_map[r['label']])
    cost_ids=sorted([r['queryId'] for r in old],key=lambda q:hashlib.sha256(('argon-ce-cost-v1|'+q).encode()).digest())[:16]
    metadata={'source':spec,'python':platform.python_version(),'torch':torch.__version__,'transformers':transformers.__version__,
              'threads':4,'device':'CPU','dtype':'float32','attention':'sdpa','maxLength':256,'batchSize':32,
              'plannedIds':[r['queryId'] for r in old],'costPanelIds':cost_ids,'scorerHash':index.model_hash,
              'protocolSha256':digest(ROOT/'PROTOCOL.md'),'codeSha256':digest(ROOT/'neural.py'),
              'gradePolicy':'max grade per repeated pair; Exact2/Partial1/Irrelevant0; unjudged0; gain2^grade-1',
              'lexicalUnionGivenForDiagnostics':True,'sharedCacheAcrossDifferentQueries':False,
              'cpu':next(s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name'))}
    (a.output/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
    predictor=Predictor(a.model,texts)
    warm=time.perf_counter()
    for _ in range(3):predictor.score('warmup query',list(range(32)))
    metadata['warmupSeconds']=time.perf_counter()-warm
    raw_count=cost_count=trace_count=0;complete=True
    with gzip.open(a.output/'raw.jsonl.gz','xt') as rawlog,gzip.open(a.output/'cost.jsonl.gz','xt') as costlog,gzip.open(a.output/'trace.jsonl.gz','xt') as tracelog:
        for oldrow in old:
            if time.perf_counter()-start>90*60:complete=False;break
            qid=oldrow['queryId'];text=qtext[qid];U=np.array(oldrow['oracleUnion'],dtype=int);grades=gold.get(qid,{})
            scores,measure=predictor.score(text,U.tolist());ordered=rank_scores(scores,U,index.ids)
            positives={pid for pid,g in grades.items() if g>=1};exact={pid for pid,g in grades.items() if g==2};inside={index.ids[i] for i in U}
            raw={'queryId':qid,'union':U.tolist(),'logits':scores.tolist(),'measure':measure,'top10':ordered[:10],
                 'qrel':qrel_metric(ordered,grades,index.ids),'judgedRelevantTotal':len(positives),'judgedRelevantInsideU':len(positives&inside),
                 'judgedExactTotal':len(exact),'judgedExactInsideU':len(exact&inside)}
            rawlog.write(json.dumps(raw,separators=(',',':'))+'\n');rawlog.flush();raw_count+=1
            if qid in cost_ids:
                P,_,proof=screen(index,text,2,10);cost={'queryId':qid,'union':U.tolist(),'pool':P.tolist(),'runs':[]}
                assert set(U)<=set(P)
                for repeat in range(2):
                    order=['U','P'] if (int(hashlib.sha256(qid.encode()).hexdigest(),16)+repeat)%2==0 else ['P','U']
                    outputs={}
                    for name in order:
                        docs=U if name=='U' else P
                        measured_start=time.perf_counter()
                        s,m=predictor.score(text,docs.tolist());rnk=rank_scores(s,docs,index.ids)
                        m['seconds']=time.perf_counter()-measured_start
                        cost['runs'].append({'repeat':repeat,'method':name,**m,'top10':rnk[:10],
                                             'qrel':qrel_metric(rnk,grades,index.ids),'logits':s.tolist()})
                        outputs[name]=s
                    mapping={d:i for i,d in enumerate(P)}
                    common=np.array([outputs['P'][mapping[d]] for d in U]);diff=float(np.max(np.abs(common-outputs['U']),initial=0))
                    cost.setdefault('maxOverlapScoreDifference',[]).append(diff)
                costlog.write(json.dumps(cost,separators=(',',':'))+'\n');costlog.flush();cost_count+=1
            # Shared exact pair trace: ordinary full-corpus incremental control
            # versus a precomputed-U view, with identical neural inputs required.
            setup=time.perf_counter();full=IncrementalScorer(index,text,10);full_setup=time.perf_counter()-setup
            setup=time.perf_counter();view=View(index,U);small=IncrementalScorer(view,text,10);small_setup=time.perf_counter()-setup
            cache={};requests=[];neural_seconds=full_seconds=small_seconds=0.;uncached_pairs=0
            for request in oldrow['requests']:
                query=request['text'];t=time.perf_counter();d1=full.query(query);full_seconds+=time.perf_counter()-t
                t=time.perf_counter();d2=U[small.query(query)];small_seconds+=time.perf_counter()-t
                np.testing.assert_array_equal(d1,d2)
                unseen=[int(d) for d in d1 if (query,int(d)) not in cache]
                sc,m=predictor.score(query,unseen);neural_seconds+=m['seconds'];uncached_pairs+=len(unseen)
                cache.update({(query,d):float(s) for d,s in zip(unseen,sc)})
                z=[cache[(query,int(d))] for d in d1];ranked=rank_scores(z,d1,index.ids)
                requests.append({'textSha256':hashlib.sha256(query.encode()).hexdigest(),'state':request['state'],
                                 'lexicalTopIds':d1.tolist(),'logits':z,'neuralTop10':ranked[:10],
                                 'newPairs':len(unseen),'qrel':qrel_metric(ranked,grades,index.ids)})
            trace={'queryId':qid,'requests':requests,'neuralPairsFullControl':uncached_pairs,'neuralPairsGivenUnion':uncached_pairs,
                   'neuralSecondsSharedExactTrace':neural_seconds,'fullLexicalSetupSeconds':full_setup,'givenUnionLexicalSetupSeconds':small_setup,
                   'fullLexicalRequestSeconds':full_seconds,'givenUnionLexicalRequestSeconds':small_seconds,
                   'scope':'Given precomputed union; not total initialization or end-to-end acceleration'}
            tracelog.write(json.dumps(trace,separators=(',',':'))+'\n');tracelog.flush();trace_count+=1
            print('neural',raw_count,'/128',qid,'U',len(U),'cost',qid in cost_ids,'tracepairs',uncached_pairs,
                  'elapsed',round(time.perf_counter()-start,1),flush=True)
    metadata.update({'status':'COMPLETE' if complete else 'RESOURCE_UNKNOWN','rawQueries':raw_count,'costQueries':cost_count,'traceQueries':trace_count,
                     'wallSeconds':time.perf_counter()-start,'fileHashes':{n:digest(a.output/n) for n in ['raw.jsonl.gz','cost.jsonl.gz','trace.jsonl.gz']}})
    (a.output/'metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')


if __name__=='__main__':main()
