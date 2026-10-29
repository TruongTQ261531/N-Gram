"""Budgeted exhaustive reference, used only below explicit resource caps."""
import itertools
import numpy as np

def state_count(sizes,budget):
 dp=[1]+[0]*budget
 for n in sizes:
  dp=[dp[b]+(dp[b-1]*(n-1) if b else 0) for b in range(budget+1)]
 return sum(dp)

def exhaustive_count(D,Du,budget,max_states=2000,max_cells=2_000_000):
 m=D[0].shape[1] if D else 0;n=len(D);sizes=[len(d) for d in D];count=state_count(sizes,budget)
 if count>max_states or count*max(1,m)>max_cells:return {'skipped':'enumeration_resource_cap','states':count,'cells':count*m}
 raw=np.zeros(m)
 for d in Du:raw=np.nextafter(raw+d[0],np.inf)
 best=int((raw>=0).sum());choices_best=np.zeros(n,dtype=int)
 for changed in range(1,min(n,budget)+1):
  for positions in itertools.combinations(range(n),changed):
   for values in itertools.product(*[range(1,sizes[i]) for i in positions]):
    value=raw.copy()
    for i,a in zip(positions,values):
     value=np.nextafter(value-Du[i][0],np.inf);value=np.nextafter(value+Du[i][a],np.inf)
    rank_count=int((value>=0).sum())
    if rank_count>best:
     best=rank_count;choices_best=np.zeros(n,dtype=int)
     for i,a in zip(positions,values):choices_best[i]=a
 return {'upper_count':best,'rank_upper':best+1,'states':count,'choices':choices_best.tolist()}
