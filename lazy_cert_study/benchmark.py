"""Development/locked-confirmation audit of whole-corpus lazy projection.

All methods retain the same scorer and receive the same request sequences.
Original input files and old study artifacts are never modified.
"""
from pathlib import Path
import argparse
import gzip
import hashlib
import itertools
import json
import pickle
import resource
import sys
import time
import os
import platform
import subprocess
from datetime import datetime,timezone

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent))
from lazy_cert_study.core import screen, materialize, lattice, IncrementalScorer, topk, zero_witness, feature_projection
from pool_study.core import normalize
sys.path.insert(0,str(ROOT.parent/'exact_pool_study'))
from method import compiled_pool,exact_from_pool
import numpy as np
import pandas as pd
from scipy import sparse
import scipy
import sklearn


class View:
    def __init__(self,index,documents,features=None):
        self.vectorizer=index.vectorizer
        if len(documents)==index.n and np.array_equal(documents,np.arange(index.n)):
            self.transpose=index.transpose
        elif features is None:
            self.transpose=index.weights[documents].T.tocsr()
        else:
            columns=np.unique(features.indices)
            local=feature_projection(index,columns,documents).tocoo()
            self.transpose=sparse.csr_matrix((local.data,(columns[local.row],local.col)),
                shape=(index.transpose.shape[0],len(documents)))
    def score(self,text):
        return (self.vectorizer.transform([text])@self.transpose).toarray()[0]


def build(index,text,kind,budget,k):
    if kind not in ('parent','screened','batch','screen_batch'):
        raise ValueError('Unknown certificate method')
    if budget not in (0,1,2) or not 1<=k<=index.n:
        raise ValueError('This audited exact pipeline supports B=0/1/2 and 1<=k<=N')
    started=time.perf_counter()
    Q=lattice(index,text)
    trivial=zero_witness(Q,budget)
    if trivial is not None:
        final=np.arange(index.n)
        raw=(Q.raw_features@index.transpose).toarray()[0]
        return final,raw,{'kind':kind,'status':'exact','pool':final.tolist(),
                         'scoreCells':0,'initialPool':index.n,'states':1,
                         'termination':'all_zero_witness','witness':trivial,
                         'seconds':time.perf_counter()-started}
    if kind in ('batch','screen_batch'):
        initial=np.arange(index.n)
        if kind=='screen_batch':
            initial,Q,proof=screen(index,text,budget,k,prepared=Q)
            if np.array_equal(initial,topk(proof['rawScores'],k)):
                return initial,proof['rawScores'][initial],{
                    'kind':kind,'status':'exact','pool':initial.tolist(),
                    'scoreCells':0,'initialPool':len(initial),'states':1,
                    'termination':'raw_pool_saturation','seconds':time.perf_counter()-started}
        view=View(index,initial,Q.feature_rows)
        count=state_count(Q.forms,budget)
        if count*len(initial)>50_000_000:
            return initial,view.score(text),{'kind':kind,'status':'resource_unknown',
                'pool':initial.tolist(),'initialPool':len(initial),'states':0,
                'theoreticalStates':count,'scoreCells':0,'capCells':50_000_000,
                'seconds':time.perf_counter()-started}
        union=np.zeros(len(initial),dtype=bool);visited=0
        stream=iter(states(Q.forms,budget));batch_size=max(1,min(2048,2_000_000//len(initial)))
        while True:
            batch=list(itertools.islice(stream,batch_size))
            if not batch:break
            texts=[' '.join(f[a]['text'] for f,a in zip(Q.forms,state)) for state in batch]
            scores=(index.vectorizer.transform(texts)@view.transpose).toarray()
            cut=np.partition(scores,-k,axis=1)[:,-k]
            union|=(scores>=cut[:,None]).any(axis=0);visited+=len(batch)
            if union.all():break
        final=initial[union]
        return final,view.score(text)[union],{'kind':kind,'status':'exact',
            'pool':final.tolist(),'initialPool':len(initial),'states':visited,
            'theoreticalStates':count,'scoreCells':visited*len(initial),
            'termination':'pool_saturation' if union.all() else 'complete_enumeration',
            'seconds':time.perf_counter()-started}
    if kind=='screened':
        initial,Q,proof=screen(index,text,budget,k,prepared=Q)
        if np.array_equal(initial,topk(proof['rawScores'],k)):
            return initial,proof['rawScores'][initial],{
                'kind':kind,'status':'exact','pool':initial.tolist(),
                'scoreCells':0,'initialPool':len(initial),'states':1,
                'termination':'raw_pool_saturation','seconds':time.perf_counter()-started}
        F,cells=materialize(index,Q,initial)
        fs=Q.forms
    else:
        fs=Q.forms
        initial=np.arange(index.n)
        F,cells=materialize(index,Q,initial)
        proof={'seconds':0.,'coarsePool':index.n}
    projected=time.perf_counter()
    pool,_=compiled_pool(F,budget,k)
    exact,_=exact_from_pool(F,pool,fs,budget=budget,k=k)
    final=initial[np.asarray(exact['pool'],dtype=int)]
    base_scores=sum(f[0] for f in F)[np.asarray(exact['pool'],dtype=int)]
    elapsed=time.perf_counter()-started
    detail={'kind':kind,'status':exact['status'],'pool':final.tolist(),
            'scoreCells':cells,'initialPool':len(initial),
            'materializeAndScreenSeconds':projected-started,
            'refinementSeconds':elapsed-(projected-started),'seconds':elapsed,
            'states':exact['states'],'theoreticalStates':exact.get('theoreticalStates'),
            'screenSeconds':proof['seconds']}
    return final,base_scores,detail


def requests(forms,qid,budget):
    seed=int(hashlib.sha256(('lazy-session-v1|'+qid).encode()).hexdigest()[:16],16)
    rng=np.random.default_rng(seed);active=[i for i,f in enumerate(forms) if len(f)>1]
    seen=set();out=[]
    for cost in [0]+[1]*6+[budget]*13:
        accepted=False
        for attempt in range(200):
            state=[0]*len(forms)
            n=min(cost,len(active))
            if n:
                for i in rng.choice(active,size=n,replace=False):
                    state[i]=int(rng.integers(1,len(forms[i])))
            text=normalize(' '.join(f[a]['text'] for f,a in zip(forms,state)))
            if text not in seen:
                seen.add(text);out.append({'text':text,'state':state});accepted=True;break
        if not accepted:continue
    if not out:raise AssertionError('Raw state must exist')
    distinct=len(out)
    return [out[i%distinct] for i in range(20)],distinct


def state_count(forms,budget):
    return int(sum(sum(np.prod([len(forms[t])-1 for t in positions],dtype=np.int64)
                        for positions in itertools.combinations(range(len(forms)),cost))
                    for cost in range(min(budget,len(forms))+1)))


def states(forms,budget):
    for cost in range(min(budget,len(forms))+1):
        for positions in itertools.combinations(range(len(forms)),cost):
            for alternatives in itertools.product(*(range(1,len(forms[t])) for t in positions)):
                state=[0]*len(forms)
                for t,a in zip(positions,alternatives):state[t]=a
                yield state


def oracle(index,forms,budget,k,max_cells=50_000_000):
    theoretical=state_count(forms,budget)
    if theoretical*index.n>max_cells:
        return None,{'status':'resource_unknown','states':int(theoretical),'capCells':max_cells}
    union=np.zeros(index.n,dtype=bool);visited=0
    # Independent recursive construction with a remaining-budget guard.
    def states(position,left,prefix):
        if position==len(forms):
            yield prefix;return
        for a in range(len(forms[position])):
            cost=int(a!=0)
            if cost<=left:yield from states(position+1,left-cost,prefix+[a])
    for state in states(0,budget,[]):
        text=' '.join(f[a]['text'] for f,a in zip(forms,state))
        union[topk(index.score(text),k)]=True;visited+=1
    assert visited==theoretical
    return np.flatnonzero(union),{'status':'exact','states':visited,'capCells':max_cells}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--phase',choices=['development','confirmation'],required=True)
    parser.add_argument('--limit',type=int)
    parser.add_argument('--repeats',type=int,default=3)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('Refusing to overwrite '+str(args.output))
    if args.phase=='confirmation':
        if args.limit is not None:raise ValueError('No partial selected confirmation')
        if args.repeats!=3:raise ValueError('Frozen confirmation requires three repeats')
        freeze=json.loads((ROOT/'confirmation_freeze.json').read_text())
        for name,h in freeze['files'].items():
            assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==h,name
        tracked=subprocess.check_output(['git','ls-files','--error-unmatch',
            'lazy_cert_study/confirmation_freeze.json'],cwd=ROOT.parent,text=True)
        assert tracked.strip()=='lazy_cert_study/confirmation_freeze.json'
        subprocess.run(['git','diff','--exit-code','HEAD','--',*freeze['files'],
            'lazy_cert_study/confirmation_freeze.json'],cwd=ROOT.parent,check=True)
    selection=json.loads((ROOT/'selection.json').read_text())
    ids=selection[args.phase]
    if args.limit is not None:ids=ids[:args.limit]
    q=pd.read_csv(args.data/'dataset/query.csv',sep='\t',dtype={'query_id':str}).fillna('')
    texts=dict(zip(q.query_id,q['query']))
    load_started=time.perf_counter()
    with (args.data/'index.pkl').open('rb') as f:index=pickle.load(f)
    load_seconds=time.perf_counter()-load_started
    receipt=json.loads((args.data/'index-receipt.json').read_text())
    assert receipt['modelHash']==index.model_hash
    # Query-independent index statistic, constructed once with the shared warm
    # index. Do not rescan all index weights inside each screened query.
    stat_started=time.perf_counter()
    index._certificate_max_weight=int(index.weights.data.max(initial=0))
    statistic_seconds=time.perf_counter()-stat_started
    args.output.parent.mkdir(parents=True,exist_ok=True)
    metadata={'startedUTC':datetime.now(timezone.utc).isoformat(),'phase':args.phase,
        'gitRevision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip(),
        'selectedIds':ids,'repeats':args.repeats,'modelHash':index.model_hash,
        'sources':json.loads((ROOT/'sources.json').read_text()),
        'sourceHashes':{str(p.relative_to(ROOT.parent)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in list(ROOT.glob('*.py'))+[ROOT/'PROTOCOL.md',ROOT/'selection.json']},
        'python':platform.python_version(),'numpy':np.__version__,'pandas':pd.__version__,
        'scipy':scipy.__version__,'scikitLearn':sklearn.__version__,
        'threadEnvironment':{k:os.environ.get(k) for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']},
        'cpuQuota':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),
        'memoryCapBytes':int(Path('/sys/fs/cgroup/memory.max').read_text()),
        'warmIndex':True,'indexBuildReceipt':receipt,'indexLoadSeconds':load_seconds,
        'sharedMaximumWeightSeconds':statistic_seconds}
    meta_path=args.output.with_name(args.output.name+'.metadata.json')
    with meta_path.open('x') as f:json.dump(metadata,f,indent=2)
    with gzip.open(args.output,'wt',encoding='utf-8') as log:
        for qi,qid in enumerate(ids):
            text=texts[qid]
            assert hashlib.sha256(text.encode()).hexdigest()==selection['querySha256'][qid]
            Q=lattice(index,text)
            sequence,distinct=requests(Q.forms,qid,2)
            gold,oracle_record=oracle(index,Q.forms,2,10)
            # Ground truth outside timing, same immutable index for all methods.
            expected=[topk(index.score(x['text']),10).tolist() for x in sequence]
            result={'queryId':qid,'querySha256':selection['querySha256'][qid],
                    'tokens':len(Q.forms),'uniqueRequests':distinct,'oracle':oracle_record,
                    'oracleUnion':None if gold is None else gold.tolist(),
                    'requests':sequence,'scenarios':{},'modelHash':index.model_hash}
            for scenario,seq in [('distinct',sequence),('repeated',sequence[:10]+sequence[:10])]:
                expected_seq=expected if scenario=='distinct' else expected[:10]+expected[:10]
                times=[]
                for repeat in range(args.repeats):
                    names=['memo','incremental','batch','parent','screened','screen_batch']
                    offset=(qi+repeat)%len(names);order=names[offset:]+names[:offset]
                    for kind in order:
                        started=time.perf_counter();memo={};detail=None
                        if kind in ['parent','screened','batch','screen_batch']:
                            pool,base,detail=build(index,text,kind,2,10)
                            view=View(index,pool,Q.feature_rows)
                            scorer=IncrementalScorer(view,text,10,base_scores=base)
                        elif kind=='incremental':scorer=IncrementalScorer(index,text,10)
                        outputs=[];prefix={}
                        for count,x in enumerate(seq,1):
                            request=x['text']
                            if kind=='memo':
                                if request not in memo:memo[request]=topk(index.score(request),10)
                                answer=memo[request]
                            elif kind=='incremental':answer=scorer.query(request)
                            else:answer=pool[scorer.query(request)]
                            outputs.append(answer.tolist())
                            if count in [1,5,20]:prefix[str(count)]=time.perf_counter()-started
                        # Exclude validation from reported timing.
                        elapsed=time.perf_counter()-started
                        if detail is not None and gold is not None:
                            if detail['status']=='exact':np.testing.assert_array_equal(pool,gold)
                            else:assert set(gold)<=set(pool)
                        assert outputs==expected_seq,(qid,kind)
                        times.append({'method':kind,'repeat':repeat,'order':order,
                                      'prefixSeconds':prefix,'seconds':elapsed,
                                      'build':detail,
                                      'answerSha256':hashlib.sha256(json.dumps(outputs,separators=(',',':')).encode()).hexdigest()})
                result['scenarios'][scenario]=times
            result['peakProcessMiB']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
            log.write(json.dumps(result,separators=(',',':'))+'\n');log.flush()
            print(args.phase,qi+1,'/',len(ids),'id',qid,'tokens',len(Q.forms),
                  'oracle',oracle_record['status'],'pool',None if gold is None else len(gold),flush=True)
    metadata['finishedUTC']=datetime.now(timezone.utc).isoformat()
    metadata['outputSha256']=hashlib.sha256(args.output.read_bytes()).hexdigest()
    meta_path.write_text(json.dumps(metadata,indent=2)+'\n')


if __name__=='__main__':main()
