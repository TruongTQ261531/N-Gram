"""Verification-only exhaustive enclosure on method-discordant queries.

Larger verifier caps NEVER change reported method bounds or primary timings.
This is retrospective auditing, not an extra certification method in the table.
It reuses the frozen screening and margin-enclosure model; it does not
independently re-prove those components or the compiled numerical libraries.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import argparse
import gzip
import itertools
import json
import numpy as np
from reviewer_audit_2026_10_31.retention import load_inputs,context,normalize,native


def exhaustive_enclosure(Du,budget=2,max_states=2_000_000,max_cells=500_000_000):
    if budget not in (0,1,2):raise ValueError('Only budgets0/1/2 are implemented')
    sizes=[len(d) for d in Du];n=len(Du);m=Du[0].shape[1] if n else 0
    count=1+(sum(s-1 for s in sizes) if budget else 0)
    if budget>=2:count+=sum((sizes[i]-1)*(sizes[j]-1) for i in range(n) for j in range(i+1,n))
    if count>max_states or count*max(1,m)>max_cells:
        return {'status':'RESOURCE_UNKNOWN','states':count,'cells':count*m}
    raw=np.zeros(m)
    for d in Du:raw=np.nextafter(raw+d[0],np.inf)
    best=int((raw>=0).sum());witness=[0]*n;visited=0
    def descriptors():
        yield (-1,0,-1,0)
        if budget:
            for t in range(n):
                for a in range(1,sizes[t]):yield (t,a,-1,0)
        if budget>=2:
            for t in range(n):
                for u in range(t+1,n):
                    for a in range(1,sizes[t]):
                        for b in range(1,sizes[u]):yield (t,a,u,b)
    batch_size=max(1,min(4096,2_000_000//max(1,m)))
    stream=iter(descriptors())
    while True:
        batch=list(itertools.islice(stream,batch_size))
        if not batch:break
        desc=np.asarray(batch,dtype=int);values=np.tile(raw,(len(batch),1))
        for slot in [0,2]:
            for t in np.unique(desc[:,slot]):
                if t<0:continue
                rows=np.flatnonzero(desc[:,slot]==t);alternatives=desc[rows,slot+1]
                values[rows]=np.nextafter(np.nextafter(values[rows]-Du[t][0],np.inf)+Du[t][alternatives],np.inf)
        counts=(values>=0).sum(axis=1)
        row=int(counts.argmax())
        if int(counts[row])>best:
            best=int(counts[row]);witness=[0]*n
            for slot in [0,2]:
                t=desc[row,slot]
                if t>=0:witness[t]=int(desc[row,slot+1])
        visited+=len(batch)
    assert visited==count
    return {'status':'COMPLETE','states':visited,'cells':visited*m,'rankUpper':best+1,
        'upperEnvelopeMaximizer':witness,'interpretation':'Max over upper-margin enclosures; not an attack witness.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--runs',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    result=[]
    for ds in ['scifact','nfcorpus','fiqa']:
        with gzip.open(args.runs/(ds+'.jsonl.gz'),'rt') as f:rows=[json.loads(l) for l in f]
        selected=[]
        for row in rows:
            first={r['method']:r for r in row['runs'] if r['repeat']==0}
            if len({r['rankUpper']<=10 for r in first.values()})>1:
                selected.append((row,first))
        if not selected:continue
        index,texts,model_hash=load_inputs(args.data,ds)
        for row,first in selected:
            text=' '.join(normalize(texts[row['queryId']]).split()[:32]);C=context(index,text,2)
            assert not C['zero']
            audit=exhaustive_enclosure(C['Du'])
            certificate=bool(audit.get('rankUpper',index.n)<=10)
            record={'dataset':ds,'queryId':row['queryId'],'bestLpRank':first['best_lp_enum']['rankUpper'],
                'discreteRank':first['discrete']['rankUpper'],
                'milpRank':first['milp_enum']['rankUpper'],'audit':audit,'enclosureCertifiesK10':certificate,
                'modelFingerprint':model_hash,'primaryBoundsAndTimesUnchanged':True}
            result.append(record);print(ds,row['queryId'],audit['status'],'verified',certificate,flush=True)
        del index
    report={'kind':'Retrospective verification-only audit of ALL coverage-discordant queries among three methods',
        'sharedAssumptions':'Uses the same frozen screening and margin enclosures; not independent validation of sparse libraries or screening',
        'records':result,
        'queries':len(result),'enclosureCertified':sum(r['enclosureCertifiesK10'] for r in result),
        'notUsedToModifyPrimaryResults':True}
    args.output.write_text(json.dumps(native(report),indent=2)+'\n')


if __name__=='__main__':main()
