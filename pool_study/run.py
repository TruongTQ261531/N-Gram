from pathlib import Path
import argparse,gzip,hashlib,json,pickle,platform,resource,sys,time
import numpy as np
import pandas as pd
import scipy,sklearn
from core import Index,candidate_pools,choices,oracle,normalize

ROOT=Path(__file__).resolve().parent

def dump(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False))

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--dataset',choices=['arguana','scidocs'],required=True);a=p.parse_args()
    frozen=json.loads((ROOT/'freeze.json').read_text())
    for name,h in frozen['files'].items():assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==h,name
    ds=a.dataset;out=ROOT/'results'/ds
    if out.exists():raise RuntimeError('Refusing to overwrite recorded results: '+str(out))
    out.mkdir(parents=True)
    for source in json.loads((ROOT/'sources.json').read_text()):
        if source['dataset']==ds:assert hashlib.sha256((a.data/ds/source['path']).read_bytes()).hexdigest()==source['sha256']
    c=pd.read_parquet(a.data/ds/'corpus/corpus-00000-of-00001.parquet').fillna('')
    q=pd.read_parquet(a.data/ds/'queries/queries-00000-of-00001.parquet').fillna('')
    docs=[{'id':str(x['_id']),'title':str(x.get('title','')),'text':str(x['text'])} for x in c.to_dict('records')]
    texts={str(x['_id']):str(x['text']) for x in q.to_dict('records')}
    selected=json.loads((ROOT/'selection.json').read_text())[ds]['queryIds']
    build=time.perf_counter();I=Index(docs);build=time.perf_counter()-build
    # Local index allows independent source replay without another build.
    with (a.data/(ds+'-index.pkl')).open('wb') as f:pickle.dump(I,f,protocol=5)
    corpus_hash=hashlib.sha256(json.dumps(I.documents,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
    dump(out/'environment.json',{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'platform':platform.platform(),'indexSeconds':build,'modelHash':I.model_hash,'corpusHash':corpus_hash,'documents':I.n,'features':I.weights.shape[1],'nnz':int(I.weights.nnz),'threads':1})
    with gzip.open(out/'records.jsonl.gz','wt',encoding='utf-8') as log:
        for qi,qid in enumerate(selected):
            start=time.perf_counter();forms,F,metadata=I.factors(texts[qid]);factor_seconds=time.perf_counter()-start
            raw=sum(f[0] for f in F);np.testing.assert_array_equal(raw,I.score(' '.join(f[0]['text'] for f in forms)))
            factor_file=f'factors-{qi:03}.npz'
            np.savez_compressed(out/factor_file,**{'f'+str(t):f for t,f in enumerate(F)})
            row={'dataset':ds,'queryId':qid,'query':texts[qid],'forms':forms,'metadata':metadata,'factorSeconds':factor_seconds,'factorFile':factor_file,'factorSha256':hashlib.sha256((out/factor_file).read_bytes()).hexdigest(),'modelHash':I.model_hash,'cases':[]}
            # Full-query re-encoding on ALL states, independently of factor additivity.
            all_choices=list(choices([len(f) for f in F],2));perturbed=[' '.join(fs[v]['text'] for fs,v in zip(forms,choice)) for choice in all_choices]
            check=time.perf_counter()
            for off in range(0,len(all_choices),64):
                direct=(I.vectorizer.transform(perturbed[off:off+64])@I.transpose).toarray()
                for z,choice in zip(direct,all_choices[off:off+64]):np.testing.assert_array_equal(z,sum(f[v] for f,v in zip(F,choice)))
            row['fullQueryReencodingSeconds']=time.perf_counter()-check
            for budget in (1,2):
                s=time.perf_counter();truth,traces=oracle(F,budget);oracle_seconds=time.perf_counter()-s
                sequence=sorted(traces,key=lambda x:hashlib.sha256((ds+'|'+qid+'|'+str(x['choices'])).encode()).digest())[:20]
                query_batch=[' '.join(fs[v]['text'] for fs,v in zip(forms,x['choices'])) for x in sequence]
                trace_name=f'oracle-{qi:03}-b{budget}.json.gz'
                with gzip.open(out/trace_name,'wt') as f:json.dump(traces,f,separators=(',',':'))
                for k in (5,10):
                    pools,proof=candidate_pools(F,budget,k)
                    repeats=[]
                    for rep in range(3):
                        s=time.perf_counter();repeated,_=candidate_pools(F,budget,k,include_fixed=False);repeats.append(time.perf_counter()-s)
                        for name,value in repeated.items():np.testing.assert_array_equal(value,pools[name])
                    gold=set(truth[k])
                    for name,pool in pools.items():assert gold<=set(pool),(ds,qid,budget,k,name)
                    pool=pools['partitioned'];s=time.perf_counter();cached=I.weights[pool].T.tocsr();cache_build_seconds=time.perf_counter()-s
                    direct_times=[];cached_times=[]
                    for rep in range(3):
                        order=['full','cached'] if (qi+budget+k+rep)%2 else ['cached','full']
                        for method in order:
                            s=time.perf_counter()
                            for text in query_batch:
                                z=I.score(text) if method=='full' else (I.vectorizer.transform([text])@cached).toarray()[0]
                                threshold=np.partition(z,-k)[-k];np.flatnonzero(z>=threshold)
                            (direct_times if method=='full' else cached_times).append((time.perf_counter()-s)/len(query_batch))
                    delta=float(np.median(direct_times)-np.median(cached_times));initial=factor_seconds+float(np.median(repeats))+cache_build_seconds
                    case={'budget':budget,'k':k,'states':len(traces),'oracleFile':trace_name,'oracleSeconds':oracle_seconds,'oracleUnion':truth[k],
                          'pools':{name:p.tolist() for name,p in pools.items()},'proof':proof,'pipelineSeconds':repeats,
                          'fullSparsePerEditSeconds':direct_times,'poolSparsePerEditSeconds':cached_times,'measuredEdits':len(sequence),
                          'cacheIndexBuildSeconds':cache_build_seconds,'timingOrder':'balanced by query, budget, k and repetition',
                          'breakEvenEdits':int(np.ceil(initial/delta)) if delta>0 else None,'initialSeconds':initial}
                    row['cases'].append(case)
            row['seconds']=time.perf_counter()-start;row['peakProcessMiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
            log.write(json.dumps(row,ensure_ascii=False,separators=(',',':'))+'\n');log.flush()
            print(ds,qi+1,'/',len(selected),'states',len(all_choices),'seconds',round(row['seconds'],3),'pools',[(r['budget'],r['k'],len(r['pools']['coupled']),len(r['pools']['partitioned']),len(r['oracleUnion'])) for r in row['cases']],flush=True)

if __name__=='__main__':main()
