"""Optional label-free refinement using complete pair proofs + standard DSATUR.

Keeps historical methods untouched. This specializes established graph bounds;
it is not claimed as a new graph-coloring algorithm or independent confirmation.
"""
import itertools,time
from reviewer_audit_2026_10_31.retention import native
from compatibility import incompatible
from argon_followup_2026_11_01.graph import complement,greedy


def pairwise_refine(D,Du,current_rank,budget=2,k=10,max_candidates=80,seconds=120.):
    n=D[0].shape[1] if D else 0
    if current_rank<=k:return {'rankUpper':current_rank,'status':'already_certified'}
    if n>max_candidates:return {'rankUpper':current_rank,'status':'candidate_cap'}
    start=time.perf_counter();checks=[];complete=True
    for i,j in itertools.combinations(range(n),2):
        if time.perf_counter()-start>seconds:complete=False;break
        result=incompatible([d[:,[i,j]] for d in D],[u[:,[i,j]] for u in Du],budget)
        checks.append(native({**result,'left':i,'right':j}))
    edges=[(r['left'],r['right']) for r in checks if r['incompatible']]
    groups=greedy(complement(n,edges));rank=min(current_rank,len(groups)+1)
    return {'rankUpper':rank,'status':'complete_pairs' if complete else 'construction_cap',
            'groups':groups,'checks':checks,'seconds':time.perf_counter()-start,
            'usesVerifiedLabels':False}
