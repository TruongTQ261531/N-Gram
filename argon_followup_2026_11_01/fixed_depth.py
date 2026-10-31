"""Actual standard BM25-depth reranking and separately scoped static-pool checks."""
import argparse,gzip,hashlib,json,pickle,time
from pathlib import Path
import numpy as np
import pandas as pd
from argon_followup_2026_11_01.neural import rank_scores,qrel_metric
from argon_followup_2026_11_01.neural_bucket import BucketPredictor
from lazy_cert_study.core import topk

ROOT=Path(__file__).resolve().parent


def read(path):
    with gzip.open(path,'rt') as f:return [json.loads(s) for s in f]


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--model',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    spec=json.loads((ROOT/'MODEL_SOURCE.json').read_text())
    for f in spec['files']:assert hashlib.sha256((a.model/f['name']).read_bytes()).hexdigest()==f['sha256']
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    old=read(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz');lex={r['queryId']:r for r in read(ROOT/'results/lexical-full-trace.jsonl.gz')}
    with gzip.open(ROOT/'results/judgments.json.gz','rt') as f:label=json.load(f)
    assert index.model_hash==label['modelHash'] and index.ids==label['documentIds']
    meta=json.loads((ROOT/'results/neural-fp32-bucket/metadata.json').read_text());panel=set(meta['costPanelIds'])
    query=pd.read_csv(a.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('');queries=dict(zip(query.query_id,query['query']))
    products=pd.read_csv(a.data/'dataset/product.csv',sep='\t',dtype={'product_id':str}).fillna('')
    texts={str(r['product_id']):' '.join(str(r[k]) for k in ['product_name','product_class','product_description']) for r in products.to_dict('records')}
    predictor=BucketPredictor(a.model,[texts[i] for i in index.ids])
    for _ in range(3):predictor.score('warmup query',list(range(32)))
    with gzip.open(a.output,'xt') as out:
        for number,r in enumerate(old,1):
            qid=r['queryId'];text=queries[qid];raw=index.score(text)
            pools={'T50':topk(raw,50),'T100':topk(raw,100)}
            if qid in panel:pools['U']=np.array(r['oracleUnion'],dtype=int)
            names=list(pools);shift=int(hashlib.sha256(('fixed-depth|'+qid).encode()).hexdigest(),16)%len(names)
            order=names[shift:]+names[:shift];runs={}
            for name in order:
                t=time.perf_counter();z,m=predictor.score(text,pools[name].tolist());ranked=rank_scores(z,pools[name],index.ids);m['seconds']=time.perf_counter()-t
                runs[name]={'documents':pools[name].tolist(),'logits':z.tolist(),'top10':ranked[:10],'measure':m,
                            'qrel':qrel_metric(ranked,label['grades'].get(qid,{}),index.ids)}
            static={}
            for name in ['T50','T100']:
                candidate=set(pools[name]);targets=[set(s['lexicalTopIds']) for s in lex[qid]['states']]
                recalls=[len(c&candidate)/len(c) for c in targets]
                static[name]={'scope':'Static CLEAN pool only; ordinary per-query retrieval recomputes candidates',
                    'allStatesContained':all(x==1 for x in recalls),'worstStateRecall':min(recalls),
                    'statesWithMissingCandidates':sum(x<1 for x in recalls)}
            row={'queryId':qid,'order':order,'costPanel':qid in panel,'runs':runs,'staticReuseDiagnostic':static}
            out.write(json.dumps(row,separators=(',',':'))+'\n');out.flush()
            print('fixed depth',number,'/128',qid,flush=True)
    metadata={'status':'COMPLETE','queries':len(old),'costQueries':len(panel),'source':meta['onnxSource'],
              'backend':meta['backend'],'maxLength':256,'threads':4,'batchSize':32,'padding':meta['padding'],
              'codeSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'primaryScope':'Raw-query reranking quality and separately STATIC clean-pool completeness',
              'fileSha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}
    a.output.with_name('fixed-depth.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')


if __name__=='__main__':main()
