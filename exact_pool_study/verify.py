"""Independent projection, equivalence, oracle, witness and session verifier.

Does not import method.py or legacy ranking/certification functions.
"""
from pathlib import Path
import argparse,gzip,hashlib,itertools,json,time
import numpy as np
ROOT=Path(__file__).resolve().parent

def load_factors(directory,row):
    p=directory/row['factorFile'];assert hashlib.sha256(p.read_bytes()).hexdigest()==row['factorSha256']
    with np.load(p) as z:
        matrix=z['scores'];mapping=z['mapping']
        F=[matrix[mapping[t,:len(fs)]] for t,fs in enumerate(row['forms'])]
    assert sum(int(f.max()) for f in F)<(2**63-1)//32
    return F

def envelope(F,fixed):
    remaining=2-sum(a!=0 for a in fixed.values());base=np.zeros(F[0].shape[1],dtype=np.int64);up=[];down=[]
    for t,f in enumerate(F):
        if t in fixed:base+=f[fixed[t]]
        else:base+=f[0];up.append(f.max(0)-f[0]);down.append(f[0]-f.min(0))
    def best(g):return np.sort(np.stack(g),axis=0)[-remaining:].sum(0) if g and remaining else np.zeros_like(base)
    return base-best(down),base+best(up)

def verify_projection(F,record):
    proof=record['proof'];n=F[0].shape[1];raw=sum(f[0] for f in F)
    L,U=envelope(F,{});threshold=np.sort(L)[-10];initial=np.flatnonzero(U>=threshold)
    assert initial.tolist()==proof['independent']
    anchors=np.lexsort((np.arange(n),-raw))[:min(n,20)];assert anchors.tolist()==proof['anchors']
    counts=np.zeros(len(initial),dtype=int)
    for anchor in anchors:
        base=np.zeros(len(initial),dtype=np.int64);gain=[]
        for f in F:
            D=f[:,initial]-f[:,anchor,None];base+=D[0];gain.append(D.max(0)-D[0])
        max_margin=base+np.sort(np.stack(gain),axis=0)[-2:].sum(0)
        counts+=max_margin<0
    coupled=initial[counts<10];assert coupled.tolist()==proof['coupled']
    selected=proof['splitTokens'];assert len(selected)==min(2,len(F))
    expected={tuple(zip(selected,values)) for values in itertools.product(*(range(len(F[t])) for t in selected)) if sum(v!=0 for v in values)<=2}
    actual={tuple(tuple(x) for x in leaf['fixed']) for leaf in proof['leaves']};assert expected==actual and len(actual)==len(proof['leaves'])
    union=set()
    for leaf in proof['leaves']:
        low,high=envelope(F,dict(leaf['fixed']));cut=np.sort(low)[-10]
        pool=coupled[high[coupled]>=cut];assert pool.tolist()==leaf['pool'];assert int(cut)==leaf['threshold'];union.update(pool.tolist())
    assert sorted(union)==record['compiledPool']==record['legacyPool']
    return np.asarray(sorted(union),dtype=int)

def original_states(F):
    # Reverse position order, cost2 before cost1/raw, different from candidate.
    for t in range(len(F)-1,-1,-1):
        for u in range(t-1,-1,-1):
            for a in range(1,len(F[t])):
                for b in range(1,len(F[u])):yield [(t,a),(u,b)]
    for t in range(len(F)-1,-1,-1):
        for a in range(1,len(F[t])):yield [(t,a)]
    yield []

def verify_directory(directory):
    start=time.perf_counter();queries=original_count=quotient_count=leaves=witness_count=score_checks=0;details=[]
    with gzip.open(directory/'records.jsonl.gz','rt') as f:rows=[json.loads(x) for x in f]
    for row in rows:
        F=load_factors(directory,row);pool=verify_projection(F,row['approximations']);leaves+=len(row['approximations']['proof']['leaves'])
        projected=[f[:,pool] for f in F];base=sum(f[0] for f in projected);all_base=sum(f[0] for f in F);true_union=np.zeros(len(pool),dtype=bool);visited=0
        stream=iter(original_states(F))
        while True:
            batch=list(itertools.islice(stream,2048))
            if not batch:break
            score=np.tile(base,(len(batch),1))
            for i,edits in enumerate(batch):
                for t,a in edits:score[i]+=projected[t][a]-projected[t][0]
            # Full sort rather than candidate's partial partition.
            cut=np.sort(score,axis=1)[:,-10];true_union|=(score>=cut[:,None]).any(0);visited+=len(batch)
        sizes=[len(f)-1 for f in F];expected=1+sum(sizes)+sum(sizes[t]*sizes[u] for t in range(len(F)) for u in range(t))
        assert visited==expected;gold=pool[true_union].tolist();original_count+=visited
        for result in row['exactModes'].values():
            if result['status']=='exact':assert result['pool']==gold
            else:assert result['status']=='resource_unknown' and result['pool']==pool.tolist()
        result=row['exactModes']['rank']
        if result['status']!='exact':queries+=1;details.append({'queryId':row['queryId'],'oracleOriginalStates':visited,'candidateStatus':'resource_unknown'});continue
        proof=row['quotientProof'];p=directory/proof['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==proof['sha256'];groups=proof['groups'];assigned=set()
        for group in groups:
            effects=np.asarray(group['effects'],dtype=np.int64);assert len(group['positions'])==len(group['representatives'])
            assert len(effects)==len({tuple(x) for x in effects.tolist()}) and all(np.any(v) for v in effects)
            for t,representatives in zip(group['positions'],group['representatives']):
                assert t not in assigned;assigned.add(t);assert len(representatives)==len(effects)
                delta=projected[t]-projected[t][0];delta-=delta[:,0,None]
                assert all(0<a<len(F[t]) for a in representatives)
                np.testing.assert_array_equal(delta[representatives],effects)
                available={tuple(v) for v in effects.tolist()}|{tuple([0]*len(pool))}
                assert all(tuple(v) in available for v in delta.tolist()),'Missing original form class'
        for t in range(len(F)):
            if t not in assigned:
                delta=projected[t]-projected[t][0];delta-=delta[:,0,None];assert not np.any(delta)
        q=[len(g['effects']) for g in groups];theoretical=1+sum(q)+sum(q[g]*q[h] for g in range(len(q)) for h in range(g))+sum(v*(v+1)//2 for v,g in zip(q,groups) if len(g['positions'])>=2)
        assert result['theoreticalStates']==theoretical
        with np.load(p) as z:descriptors=z['descriptors'];bits=np.unpackbits(z['topKBits'],axis=1,count=len(pool),bitorder='little').astype(bool)
        assert len(descriptors)==len(bits)==result['states'];assert len(np.unique(descriptors,axis=0))==len(descriptors)
        got=np.zeros(len(pool),dtype=bool)
        for offset in range(0,len(descriptors),2048):
            batch=descriptors[offset:offset+2048];score=np.tile(base,(len(batch),1))
            for i,(g,a,h,b) in enumerate(batch):
                assert (g>=0 and 0<=a<q[g]) or (g==a==-1)
                assert (h>=0 and 0<=b<q[h]) or (h==b==-1)
                assert h<0 or g>=0
                if h>=0:assert g<h or (g==h and a<=b and len(groups[g]['positions'])>=2)
                usage={}
                for group,option in [(int(g),int(a)),(int(h),int(b))]:
                    if group<0:continue
                    used=usage.get(group,0);G=groups[group];t=G['positions'][used];alt=G['representatives'][used][option]
                    score[i]+=projected[t][alt]-projected[t][0];usage[group]=used+1
            cut=np.sort(score,axis=1)[:,-10];truth=score>=cut[:,None]
            np.testing.assert_array_equal(truth,bits[offset:offset+len(batch)]);got|=truth.any(0);score_checks+=len(batch)*len(pool)
        if result['enumerationComplete']:assert len(descriptors)==theoretical
        else:assert got.all() and result['termination']=='pool_saturation'
        assert pool[got].tolist()==gold
        for doc,edits in result['witnesses'].items():
            assert len(edits)<=2 and len({t for t,a in edits})==len(edits);score=all_base.copy()
            for t,a in edits:score+=F[t][a]-F[t][0]
            assert score[int(doc)]>=np.sort(score)[-10];witness_count+=1
        expected_requests=[]
        for edits in row['sessionRequests']['edits']:
            score=all_base.copy()
            for t,a in edits:score+=F[t][a]-F[t][0]
            expected_requests.append(np.flatnonzero(score>=np.sort(score)[-10]).tolist())
        assert len(expected_requests)==20 and expected_requests==row['sessionExpectedTopK']
        h=hashlib.sha256(json.dumps(expected_requests,separators=(',',':')).encode()).hexdigest()
        assert len(row['sessions'])==12 and all(x['answerSha256']==h and x['requestCount']==20 for x in row['sessions'])
        full=row['fullCorpusOracle']
        if full['status']=='exact':assert full['pool']==gold
        quotient_count+=len(descriptors);queries+=1;details.append({'queryId':row['queryId'],'oracleOriginalStates':visited,'quotientVisited':len(descriptors),'exactUnion':len(gold)})
    return {'queries':queries,'independentOriginalProjectedStates':original_count,'quotientStatesChecked':quotient_count,'quotientScoreCellsChecked':score_checks,'conditionalLeavesChecked':leaves,'fullCorpusWitnessesChecked':witness_count,'missingOrExtraOracleDocuments':0,'allSessionAnswersEqual':True,'seconds':time.perf_counter()-start,'rows':details}

def main():
    p=argparse.ArgumentParser();p.add_argument('--dataset',choices=['arguana','scidocs'],required=True);p.add_argument('--output',type=Path);a=p.parse_args();report=verify_directory(ROOT/'results'/a.dataset)
    if a.output:a.output.write_text(json.dumps(report,indent=2))
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
