from method import compiled_pool,exact_from_pool,legacy,representative
from pathlib import Path
import argparse,gzip,hashlib,json,pickle,resource,time
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_text(json.dumps(obj,indent=2,ensure_ascii=False))

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--dataset',choices=['arguana','scidocs'],required=True);a=p.parse_args()
    freeze=json.loads((ROOT/'freeze.json').read_text())
    for name,h in freeze['files'].items():assert digest(ROOT.parent/name)==h,name
    out=ROOT/'results'/a.dataset
    if out.exists():raise RuntimeError('Refusing to overwrite '+str(out))
    out.mkdir(parents=True)
    for source in json.loads((ROOT.parent/'pool_study/sources.json').read_text()):
        if source['dataset']==a.dataset:assert digest(a.data/a.dataset/source['path'])==source['sha256']
    with (a.data/(a.dataset+'-index.pkl')).open('rb') as f:I=pickle.load(f)
    h=hashlib.sha256()
    for array in (I.weights.indptr,I.weights.indices,I.weights.data):h.update(array.astype('<i8').tobytes())
    h.update('\n'.join(I.ids).encode());h.update('\n'.join(I.vectorizer.get_feature_names_out()).encode())
    assert h.hexdigest()==I.model_hash==json.loads((ROOT.parent/'pool_study/results'/a.dataset/'environment.json').read_text())['modelHash']
    q=pd.read_parquet(a.data/a.dataset/'queries/queries-00000-of-00001.parquet');texts={str(x['_id']):str(x['text']) for x in q.to_dict('records')}
    selection=json.loads((ROOT/'selection.json').read_text())[a.dataset]
    save(out/'document-ids.json',I.ids);save(out/'environment.json',{'modelHash':I.model_hash,'documents':I.n,'source':'same pinned stored integer ranker; canonical hash independently recomputed','threads':1})
    with gzip.open(out/'records.jsonl.gz','wt',encoding='utf-8') as log:
        for qi,qid in enumerate(selection['ids']):
            started=time.perf_counter();text=texts[qid];assert hashlib.sha256(text.encode()).hexdigest()==selection['querySha256'][qid]
            t=time.perf_counter();forms,F,meta=I.factors(text,max_tokens=1_000_000);factor_time=time.perf_counter()-t;assert not meta['truncated']
            unique={};vectors=[];mapping=np.full((len(F),4),-1,dtype=np.int32)
            for pos,(fs,f) in enumerate(zip(forms,F)):
                for alt,form in enumerate(fs):
                    key=form['text']
                    if key not in unique:unique[key]=len(vectors);vectors.append(f[alt])
                    else:np.testing.assert_array_equal(vectors[unique[key]],f[alt])
                    mapping[pos,alt]=unique[key]
            factor_name=f'factors-{qi:03}.npz';np.savez_compressed(out/factor_name,scores=np.stack(vectors),mapping=mapping)
            row={'dataset':a.dataset,'queryId':qid,'query':text,'forms':forms,'metadata':meta,'factorSeconds':factor_time,'factorFile':factor_name,'factorSha256':digest(out/factor_name),'uniqueFormTexts':list(unique),'modelHash':I.model_hash,'approximations':{},'exactModes':{},'sessions':[]}
            old_times=[];new_times=[]
            for rep in range(3):
                for name in (['legacy','compiled'] if (qi+rep)%2 else ['compiled','legacy']):
                    t=time.perf_counter()
                    if name=='legacy':pools,_=legacy.candidate_pools(F,2,10,include_fixed=False);old=pools['partitioned'];old_times.append(time.perf_counter()-t)
                    else:pool,proof=compiled_pool(F);new_times.append(time.perf_counter()-t)
                np.testing.assert_array_equal(old,pool)
            row['approximations']={'legacyPool':old.tolist(),'compiledPool':pool.tolist(),'legacySeconds':old_times,'compiledSeconds':new_times,'proof':proof}
            modes=['none','score','text','rank'];outputs={};timings={name:[] for name in modes}
            for rep in range(3):
                for mode in modes[rep:]+modes[:rep]:
                    result,_=exact_from_pool(F,pool,forms,mode=mode);timings[mode].append(result['seconds']);outputs[mode]=result
            for mode,result in outputs.items():
                row['exactModes'][mode]={**result,'repeatSeconds':timings[mode]}
                if result['status']=='exact':
                    assert outputs['rank']['status']!='exact' or result['pool']==outputs['rank']['pool']
            exact,trace=exact_from_pool(F,pool,forms,mode='rank',collect=True)
            if exact['status']=='exact':
                trace_name=f'quotient-{qi:03}.npz';np.savez_compressed(out/trace_name,descriptors=trace['descriptors'],topKBits=trace['topKBits'])
                row['quotientProof']={'file':trace_name,'sha256':digest(out/trace_name),'groups':trace['groups']}
                desc=trace['descriptors'];indices=sorted(range(len(desc)),key=lambda j:hashlib.sha256((qid+'|'+str(desc[j].tolist())).encode()).digest())[:20]
                chosen=[indices[j%len(indices)] for j in range(20)]
                requests=[];choices=[]
                for index in chosen:
                    edits=representative(trace['groups'],desc[index]);aform=[0]*len(F)
                    for pos,alt in edits:aform[pos]=alt
                    requests.append(' '.join(fs[v]['text'] for fs,v in zip(forms,aform)));choices.append(edits)
                row['sessionRequests']={'descriptorIndices':chosen,'distinctDescriptors':len(set(chosen)),'edits':choices,'count':20}
                for rep in range(3):
                    names=['full','legacy','compiled','exact'];offset=(qi+rep)%4;order=names[offset:]+names[:offset]
                    baseline=None;answers={}
                    for name in order:
                        t=time.perf_counter();selected=np.arange(I.n);status='full_corpus'
                        if name!='full':
                            fs,values,_=I.factors(text,max_tokens=1_000_000)
                            if name=='legacy':selected=legacy.candidate_pools(values,2,10,include_fixed=False)[0]['partitioned'];status='safe_approximation'
                            else:
                                selected,_=compiled_pool(values);status='safe_approximation'
                                if name=='exact':
                                    z,_=exact_from_pool(values,selected,fs);selected=np.asarray(z['pool'],dtype=int);status=z['status']
                            cache=I.weights[selected].T.tocsr()
                        results=[]
                        for request in requests:
                            scores=I.score(request) if name=='full' else (I.vectorizer.transform([request])@cache).toarray()[0]
                            threshold=np.partition(scores,-10)[-10];results.append(selected[scores>=threshold].tolist())
                        elapsed=time.perf_counter()-t;answers[name]=results
                        answer_hash=hashlib.sha256(json.dumps(results,separators=(',',':')).encode()).hexdigest()
                        row['sessions'].append({'repeat':rep,'method':name,'status':status,'seconds':elapsed,'poolSize':len(selected),'requestCount':20,'order':order,'answerSha256':answer_hash})
                    for name,results in answers.items():assert results==answers['full'],(qid,name)
                    row['sessionExpectedTopK']=answers['full']
                # Verify fresh full-query scoring against factor sum on every measured request.
                raw=sum(f[0] for f in F)
                for request,edits in zip(requests,choices):
                    score=raw.copy()
                    for pos,alt in edits:score+=F[pos][alt]-F[pos][0]
                    np.testing.assert_array_equal(score,I.score(request))
            full,_=exact_from_pool(F,np.arange(I.n),forms,mode='none',max_cells=100_000_000)
            row['fullCorpusOracle']=full
            if full['status']=='exact' and exact['status']=='exact':assert full['pool']==exact['pool']
            row['seconds']=time.perf_counter()-started;row['peakProcessMiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
            log.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n');log.flush()
            print(a.dataset,qi+1,'/16','tokens',len(F),'pools',len(pool),len(exact['pool']),'states',outputs['none']['states'],exact['states'],'seconds',round(row['seconds'],2),flush=True)

if __name__=='__main__':main()
