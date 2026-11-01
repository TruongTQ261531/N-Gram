"""All-query supplemental profile: same algorithms, node guard disabled."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,gzip,hashlib,json,pickle,time
from pathlib import Path
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from utk_full_domain_2026_11_01 import run
from utk_full_domain_2026_11_01.algorithms import finite_union


def objdigest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def extended(*args,**kwargs):return finite_union(*args,**kwargs,node_cap=10**18)


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);a=p.parse_args()
    spec=json.loads((run.ROOT/'PROFILE_FREEZE.json').read_text())
    for name,sha in spec['sourceHashes'].items():assert run.digest(run.ROOT.parent/name)==sha
    assert run.digest(a.data/'index.pkl')==spec['privateIndexSha256']
    for item in json.loads((run.ROOT.parent/'lazy_cert_study/sources.json').read_text())['files']:
        assert run.digest(a.data/item['path'])==item['sha256']
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    assert index.model_hash==spec['modelHash'];index._certificate_max_weight=int(index.weights.data.max(initial=0))
    q=pd.read_csv(a.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('');texts=dict(zip(q.query_id,q['query']))
    run.finite_union=extended
    meta={'status':'RUNNING','retrospectiveSupplement':True,'repeats':1,'arrangementNodeCap':'disabled',
          'wallSeconds':120,'stateScoreCellCap':50_000_000,'oldOutcomesReadByRunner':False,
          'profileFreezeSha256':run.digest(run.ROOT/'PROFILE_FREEZE.json'),'originalCppRuntimeReproduction':False}
    output=run.ROOT/'results/profile.jsonl.gz';metadata=run.ROOT/'results/profile-metadata.json'
    metadata.write_text(json.dumps(meta,indent=2)+'\n')
    with gzip.open(output,'xt') as out:
        for i,qid in enumerate(spec['queryIds'],1):
            shift=int(hashlib.sha256(('utk-wall-only-v1|'+qid).encode()).hexdigest(),16)%4
            order=run.METHODS[shift:]+run.METHODS[:shift];runs=[]
            for method in order:
                start=time.perf_counter()
                try:
                    union,detail=run.build(index,texts[qid],method);end=time.perf_counter()
                    proof=detail.get('proof')
                    if proof and detail['status']=='exact':
                        proof['filterSha256']=objdigest(proof.pop('filter'))
                        proof['survivorFactorsSha256']=objdigest(proof.pop('survivorFactors'))
                    runs.append({'method':method,'seconds':end-start,'status':detail['status'],
                                 'union':sorted(int(j) for j in union),'receipt':detail})
                except Exception as e:runs.append({'method':method,'seconds':time.perf_counter()-start,'status':'error','errorType':type(e).__name__,'error':str(e)})
            out.write(json.dumps({'queryId':qid,'order':order,'runs':runs},separators=(',',':'))+'\n');out.flush()
            print(i,'/',len(spec['queryIds']),qid,{r['method']:(round(r['seconds'],3),r['status']) for r in runs},flush=True)
    meta.update({'status':'COMPLETE','queries':len(spec['queryIds']),'recordsSha256':run.digest(output)})
    metadata.write_text(json.dumps(meta,indent=2)+'\n')


if __name__=='__main__':
    with threadpool_limits(limits=1):main()
