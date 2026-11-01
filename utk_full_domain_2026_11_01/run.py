"""Timed full-domain matched controls; opens IDs/sources, never old outcomes."""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,gzip,hashlib,json,pickle,platform,subprocess,time
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import scipy,sklearn
from threadpoolctl import threadpool_limits,threadpool_info
from lazy_cert_study.core import lattice,screen,materialize,zero_witness,topk
from lazy_cert_study.benchmark import build as original_build,state_count
from utk_full_domain_2026_11_01.algorithms import finite_union

ROOT=Path(__file__).resolve().parent
METHODS=['screen_batch','parent','rsa_fd','jaa_fd']


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def array_digest(arrays):
    h=hashlib.sha256()
    for a in arrays:
        h.update(json.dumps(list(a.shape)).encode());h.update(np.ascontiguousarray(a,dtype=np.int64).tobytes())
    return h.hexdigest()


def build(index,text,method):
    if method in ['parent','screen_batch']:
        union,_,detail=original_build(index,text,method,2,10)
        return union,{'status':detail['status'],'summary':{k:v for k,v in detail.items() if k!='pool'}}
    start=time.perf_counter();Q=lattice(index,text);zero=zero_witness(Q,2)
    count=state_count(Q.forms,2)
    if zero is not None:
        return np.arange(index.n),{'status':'exact','termination':'all_zero_witness','theoreticalStates':count,'zeroWitness':zero}
    pool,Q,proof=screen(index,text,2,10,prepared=Q)
    receipt={'coarsePool':pool.tolist(),'anchors':proof['anchors'],'anchorLower':proof['anchorLower'],
             'threshold':proof['threshold'],'maximumExcludedUpper':int(proof['upperScores'][proof['upperScores']<proof['threshold']].max(initial=-1))}
    if np.array_equal(pool,topk(proof['rawScores'],10)):
        return pool,{'status':'exact','termination':'raw_pool_saturation','theoreticalStates':count,'screen':receipt}
    F,cells=materialize(index,Q,pool);prepared=time.perf_counter()
    local,detail=finite_union(F,2,10,method,deadline=start+120.)
    ended=time.perf_counter();status=detail.pop('status')
    detail.update({'sourceFactorSha256':array_digest(F),'poolMapping':pool.tolist()})
    return pool[np.asarray(local,dtype=int)],{'status':status,'theoreticalStates':count,'screen':receipt,
            'materializedCells':cells,'preparationSeconds':prepared-start,'refinementSeconds':ended-prepared,'proof':detail}


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    for name,sha in freeze['sourceHashes'].items():assert digest(ROOT.parent/name)==sha,name
    sources=json.loads((ROOT.parent/'lazy_cert_study/sources.json').read_text())
    for item in sources['files']:assert digest(a.data/item['path'])==item['sha256']
    assert digest(a.data/'index.pkl')==freeze['privateIndexSha256']
    with (a.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    assert index.model_hash==freeze['modelHash'] and index.n==42994
    index._certificate_max_weight=int(index.weights.data.max(initial=0))
    queries=pd.read_csv(a.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('')
    texts=dict(zip(queries.query_id,queries['query']))
    a.output.mkdir(parents=True,exist_ok=False)
    meta={'status':'RUNNING','startedUtc':datetime.now(timezone.utc).isoformat(),'retrospective':True,
          'freezeSha256':digest(ROOT/'FREEZE.json'),'modelHash':index.model_hash,
          'gitCommit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
          'methods':METHODS,'repeats':3,'oldOutcomesReadByRunner':False,'numericalThreads':1,
          'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,
          'threadpools':threadpool_info(),'cpuQuota':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
          'cpu':next(s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),
          'timingScope':'Whole pipeline including lattice/screen/factors/refinement, shared warm index excluded',
          'originalCppRuntimeReproduction':False}
    (a.output/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    with gzip.open(a.output/'records.jsonl.gz','xt') as out:
        for number,qid in enumerate(freeze['queryIds'],1):
            shift=int(hashlib.sha256(('utk-full-domain-v1|'+qid).encode()).hexdigest(),16)%4
            row={'queryId':qid,'querySha256':hashlib.sha256(texts[qid].encode()).hexdigest(),'runs':[],'receipts':{}}
            for repeat in range(3):
                order=METHODS[(shift+repeat)%4:]+METHODS[:(shift+repeat)%4]
                for method in order:
                    started=time.perf_counter()
                    try:
                        union,detail=build(index,texts[qid],method);ended=time.perf_counter()
                        encoded=json.dumps(detail,sort_keys=True,separators=(',',':'))
                        run={'repeat':repeat,'method':method,'order':order,'seconds':ended-started,
                             'status':detail['status'],'union':sorted(int(j) for j in union),
                             'termination':detail.get('termination') or detail.get('summary',{}).get('termination'),
                             'receiptSha256':hashlib.sha256(encoded.encode()).hexdigest()}
                        if repeat==0:row['receipts'][method]=detail
                    except Exception as error:
                        run={'repeat':repeat,'method':method,'order':order,'seconds':time.perf_counter()-started,
                             'status':'error','errorType':type(error).__name__,'error':str(error)}
                    row['runs'].append(run)
            out.write(json.dumps(row,separators=(',',':'))+'\n');out.flush()
            print(number,'/',len(freeze['queryIds']),qid,{m:(round(float(np.median([r['seconds'] for r in row['runs'] if r['method']==m])),3),[r['status'] for r in row['runs'] if r['method']==m]) for m in METHODS},flush=True)
    meta.update({'status':'COMPLETE','queries':len(freeze['queryIds']),'finishedUtc':datetime.now(timezone.utc).isoformat(),
                 'recordsSha256':digest(a.output/'records.jsonl.gz')})
    (a.output/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')


if __name__=='__main__':
    with threadpool_limits(limits=1):main()
