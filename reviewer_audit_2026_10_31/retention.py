"""Post hoc complete-case MILP audit and all-query timing; old code unchanged."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import math
import pickle
import sys
import time
import warnings
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits,threadpool_info

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'round3'))
from core import Index,normalize,outward_scores
from screening import coarse_candidates
from rank_bound import ranges,envelope,direct_reference
from compatibility import cover_bound
from enumeration import exhaustive_count
from mip_reference import solve as mip_solve


def native(x):
    if isinstance(x,np.ndarray):return x.tolist()
    if isinstance(x,np.generic):return native(x.item())
    if isinstance(x,float) and not math.isfinite(x):return None
    if isinstance(x,dict):return {k:native(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [native(v) for v in x]
    return x


def fingerprint(index):
    h=hashlib.sha256()
    for a in [index.W.data,index.W.indices,index.W.indptr]:
        h.update(str(a.dtype).encode());h.update(a.tobytes())
    h.update(json.dumps(index.W.shape).encode())
    h.update(json.dumps(index.ids.tolist(),ensure_ascii=False).encode())
    h.update(json.dumps(sorted(index.v.vocabulary_.items()),ensure_ascii=False).encode())
    return h.hexdigest()


def load_inputs(data,ds):
    manifest=json.loads((ROOT.parent/'round3/download_manifest.json').read_text())
    for item in manifest:
        if item['local'].split('/')[1]!=ds:continue
        p=data/item['local']
        if not p.exists():raise FileNotFoundError('Exact historical input unavailable: '+str(p))
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
    source=data/'data'/ds/'source'
    corpus=pd.read_parquet(source/'corpus/corpus-00000-of-00001.parquet').fillna('')
    query=pd.read_parquet(source/'queries/queries-00000-of-00001.parquet').fillna('')
    corpus['_id']=corpus['_id'].astype(str);query['_id']=query['_id'].astype(str)
    corpus=corpus.sort_values('_id').reset_index(drop=True)
    expected=json.loads((ROOT.parent/'round3/results/index_fingerprints.json').read_text())[ds+'_char']['sha256']
    cache=data/'cache'/(ds+'_char.pkl');cache.parent.mkdir(exist_ok=True)
    if cache.exists():
        with cache.open('rb') as f:index=pickle.load(f)
    else:
        index=Index((corpus['title']+' '+corpus['text']).map(normalize).tolist(),corpus['_id'].tolist(),'char')
        assert fingerprint(index)==expected
        with cache.open('xb') as f:pickle.dump(index,f,protocol=5)
    assert fingerprint(index)==expected
    index.transpose()
    return index,dict(zip(query['_id'],query['text'])),expected


def context(index,text,budget=2):
    query=index.query(text);ranking=query.rankings()
    coarse=coarse_candidates(query,ranking,budget)
    if coarse['zero'][budget]:return {'zero':True,'n':index.n,'query':query,'ref':coarse['ref']}
    docs=np.array([coarse['ref']]+sorted(set(coarse['keep'][budget])-{coarse['ref']}),dtype=int)
    W=index.W[docs].T.tocsr();F=[(A@W).toarray() for A in query.features]
    lo,hi=outward_scores(F,query.features)
    point,L,U=ranges(F,lo,hi,0,np.arange(1,len(docs)),budget)
    keep=U[budget]>=0;candidate=np.arange(1,len(docs))[keep]
    D=[f[:,candidate]-f[:,0,None] for f in F]
    Du=[np.nextafter(h[:,candidate]-l[:,0,None],np.inf) for l,h in zip(lo,hi)]
    return {'zero':False,'D':D,'Du':Du,'lower':L[budget,keep],
        'query':query,'docs':docs,'candidate':candidate,'ref':coarse['ref'],'n':index.n}


def kernel(D,Du,lower,kind,budget=2):
    m=len(lower);enum=exhaustive_count(D,Du,budget)
    rank=min(m+1,int(enum.get('rank_upper',m+1)))
    detail={'pairRank':m+1,'enumRank':enum.get('rank_upper'),'enumStatus':enum.get('skipped','complete')}
    if kind in ('best_lp_enum','discrete'):
        custom=envelope(D,Du,lower,budget,40)
        rank=min(rank,int(np.floor(np.nextafter(custom['upper_count'],np.inf)))+1)
        detail['customLpRank']=int(np.floor(np.nextafter(custom['upper_count'],np.inf)))+1
        detail['customLpIterations']=custom['iterations']
    if kind=='best_lp_enum':
        if sum(len(d) for d in D)*m<=2_000_000:
            direct=direct_reference(D,Du,lower,budget)
            detail['genericLpSuccess']=direct.get('success')
            if direct.get('success'):
                rank=min(rank,int(np.floor(np.nextafter(direct['upper_count'],np.inf)))+1)
        else:detail['genericLpSkipped']='matrix_entries_resource_cap'
    elif kind=='discrete':
        graph=cover_bound(D,Du,budget,120,80)
        rank=min(rank,graph['count_upper']+1)
        detail['graphRank']=graph['count_upper']+1;detail['graphSkipped']=graph.get('skipped')
    elif kind=='milp_enum':
        result=mip_solve(Du,lower,budget,1.)
        detail['milp']=result
        if result.get('count_upper') is not None:
            # Same conservative numerical rounding used by the historical control.
            rank=min(rank,int(np.floor(np.nextafter(result['count_upper']+1e-6,np.inf)))+1)
    elif kind not in ('best_lp_enum','pair_enum'):
        raise ValueError(kind)
    return rank,native(detail)


def evaluate(index,text,kind):
    started=time.perf_counter();C=context(index,text,2)
    if C['zero']:rank=index.n;detail={'zeroReference':True}
    else:rank,detail=kernel(C['D'],C['Du'],C['lower'],kind)
    elapsed=time.perf_counter()-started
    detail['candidateCount']=index.n-1 if C['zero'] else len(C['lower'])
    return rank,elapsed,detail,C


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--dataset',choices=['scifact','nfcorpus','fiqa'],required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    scope=json.loads((ROOT/'scope.json').read_text())
    for name,digest in scope['sourceFiles'].items():
        assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==digest,name
    ds=args.dataset;ids=scope['replicationIds'][ds]
    index,texts,model_hash=load_inputs(args.data,ds)
    with gzip.open(ROOT.parent/'round3/results'/(ds+'_independent_replication.jsonl.gz'),'rt') as f:
        old={row['query_id']:row for row in map(json.loads,f)}
    methods=['best_lp_enum','discrete','milp_enum']
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(args.output,'xt') as out:
        for number,qid in enumerate(ids,1):
            text=' '.join(normalize(texts[qid]).split()[:32]);runs=[]
            repeats=3 if qid in scope['timingRepeatedSubset'][ds] else 1
            for repeat in range(repeats):
                shift=(int(hashlib.sha256((ds+'|'+qid).encode()).hexdigest(),16)+repeat)%3
                order=methods[shift:]+methods[:shift]
                for kind in order:
                    rank,seconds,detail,C=evaluate(index,text,kind)
                    if kind!='milp_enum':
                        key='best_lp_enum_rank_upper' if kind=='best_lp_enum' else 'proposed_rank_upper'
                        assert rank==old[qid][key],(ds,qid,kind,rank,old[qid][key])
                    milp=detail.get('milp',{});choices=milp.get('choices')
                    witness=None
                    if choices is not None:
                        # Outside timing: full-query original-index witness replay.
                        assert sum(a!=0 for a in choices)<=2
                        z=index.score(C['query'].text(choices));ref=C['ref']
                        observed=1+int((z>z[ref]+1e-8).sum())
                        assert observed<=rank,(ds,qid,'witness exceeds returned bound')
                        witness={'strictObservedRank':observed,'choices':choices}
                    runs.append({'method':kind,'repeat':repeat,'order':order,
                        'rankUpper':rank,'seconds':seconds,'detail':detail,'witness':witness})
            row={'dataset':ds,'queryId':qid,'modelFingerprint':model_hash,
                'oldBestLpRank':old[qid]['best_lp_enum_rank_upper'],
                'oldDiscreteRank':old[qid]['proposed_rank_upper'],'runs':runs}
            out.write(json.dumps(native(row),separators=(',',':'))+'\n');out.flush()
            print(ds,number,'/',len(ids),'id',qid,'seconds',round(sum(x['seconds'] for x in runs),3),flush=True)
    metadata={'status':'COMPLETE','retrospective':True,'dataset':ds,'queries':len(ids),
        'scopeSha256':hashlib.sha256((ROOT/'scope.json').read_bytes()).hexdigest(),
        'codeSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'outputSha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'modelFingerprint':model_hash,'threadpools':threadpool_info(),
        'primaryTiming':'First balanced pass, all queries; repeats are separate noise analysis'}
    args.output.with_name(args.output.name+'.metadata.json').write_text(json.dumps(native(metadata),indent=2)+'\n')


if __name__=='__main__':
    warnings.filterwarnings('ignore',message='.*Unrecognized options.*')
    with threadpool_limits(limits=1):main()
