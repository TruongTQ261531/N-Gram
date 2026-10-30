"""Independent finite-state verifier; never imports core.py or the ranker.

Checks stored factor arithmetic, all oracle top-k traces and conditional cover.
Original-text factor reconstruction is a separate full-source replay.
"""
from pathlib import Path
import argparse,gzip,hashlib,itertools,json,time
import numpy as np
ROOT=Path(__file__).resolve().parent

def enumerate_states(sizes,b):
    # Different order/construction from the runner's changed-position oracle.
    def rec(t,left,acc):
        if t==len(sizes):yield acc;return
        for a in range(sizes[t]):
            cost=int(a!=0)
            if cost<=left:yield from rec(t+1,left-cost,acc+[a])
    return rec(0,b,[])

def verify(directory):
    start=time.perf_counter();cases=states=members=leaves=0
    detail=[]
    with gzip.open(directory/'records.jsonl.gz','rt') as f:rows=[json.loads(x) for x in f]
    for row in rows:
        p=directory/row['factorFile'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['factorSha256']
        with np.load(p) as z:F=[z['f'+str(t)] for t in range(len(row['forms']))]
        n=F[0].shape[1];assert all(v.dtype==np.int64 and v.shape[1]==n and np.all(v>=0) for v in F)
        # Ensure numpy int64 summation equals arbitrary precision for a strict
        # a-priori range, then every accumulated score fits exactly.
        assert sum(int(v.max()) for v in F)<(2**63-1)//32
        expected_anchors=np.lexsort((np.arange(n),-sum(v[0] for v in F)))
        for b in (1,2):
            selected=[x for x in row['cases'] if x['budget']==b]
            with gzip.open(directory/selected[0]['oracleFile'],'rt') as f:records=json.load(f)
            indexed={tuple(x['choices']):x['topKWithTies'] for x in records};assert len(indexed)==len(records)
            unions={k:set() for k in (5,10)};seen=0
            for a in enumerate_states([len(v) for v in F],b):
                score=np.zeros(n,dtype=np.int64)
                for v,s in zip(F,a):score+=v[s]
                stored=indexed[tuple(a)]
                for k in (5,10):
                    # Full sort, independent from the oracle's partition.
                    threshold=np.sort(score)[-k];top=np.flatnonzero(score>=threshold).tolist()
                    assert top==stored[str(k)],(row['queryId'],b,k,a)
                    unions[k].update(top);members+=len(top)
                    case=next(x for x in selected if x['k']==k)
                    for pool in case['pools'].values():
                        # Statewise equality of full and cached top-k, including ties.
                        pidx=np.asarray(pool,dtype=int)
                        local=score[pidx];cut=np.sort(local)[-k]
                        assert pidx[local>=cut].tolist()==top
                seen+=1
            assert seen==len(records);states+=seen
            for case in selected:
                k=case['k'];assert set(case['oracleUnion'])==unions[k]
                assert len(case['proof']['anchors'])==min(n,max(20,2*k))
                assert case['proof']['anchors']==expected_anchors[:min(n,max(20,2*k))].tolist()
                coupled=set(case['pools']['coupled'])
                for name,key in [('adaptive','partitioned'),('fixed','fixedPartition')]:
                    proof=case['proof'][name];tokens=proof['splitTokens']
                    assert len(tokens)==min(2,len(F)) and len(set(tokens))==len(tokens)
                    fixed_expected={tuple(zip(tokens,vals)) for vals in itertools.product(*(range(len(F[t])) for t in tokens)) if sum(v!=0 for v in vals)<=b}
                    fixed_actual={tuple(tuple(a) for a in leaf['fixed']) for leaf in proof['leaves']}
                    assert fixed_expected==fixed_actual and len(fixed_actual)==len(proof['leaves'])
                    union=set()
                    for leaf in proof['leaves']:
                        fixed=dict(leaf['fixed']);remaining=b-sum(v!=0 for v in fixed.values())
                        base=np.zeros(n,dtype=np.int64);up=[];down=[]
                        for t,v in enumerate(F):
                            if t in fixed:base+=v[fixed[t]]
                            else:
                                base+=v[0];up.append(np.max(v,axis=0)-v[0]);down.append(v[0]-np.min(v,axis=0))
                        def best(g):
                            if not g or not remaining:return np.zeros(n,dtype=np.int64)
                            return np.sort(np.asarray(g),axis=0)[-remaining:].sum(axis=0)
                        lower=base-best(down);upper=base+best(up);threshold=np.sort(lower)[-k]
                        expected=set(np.flatnonzero(upper>=threshold))&coupled
                        assert expected==set(leaf['pool']);union.update(expected);leaves+=1
                    assert union==set(case['pools'][key])
                for pool in case['pools'].values():assert unions[k]<=set(pool)
                assert set(case['pools']['partitioned'])<=coupled<=set(case['pools']['independent'])
                cases+=1
            detail.append({'queryId':row['queryId'],'budget':b,'states':seen})
    return {'queries':len(rows),'cases':cases,'states':states,'topKMembershipsChecked':members,'conditionalLeavesChecked':leaves,'missingOracleDocuments':0,'statewiseCachedFullTopKEqual':True,'seconds':time.perf_counter()-start,'rows':detail}

def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',choices=['arguana','scidocs'],required=True);p.add_argument('--output',type=Path);a=p.parse_args()
    report=verify(ROOT/'results'/a.dataset)
    if a.output:a.output.write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))

if __name__=='__main__':main()
