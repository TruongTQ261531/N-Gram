"""Numerical cross-checks on exported real-query margin matrices.
These avoid corpus/index pickles; they are not a formal machine-code proof.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,math
import numpy as np
from rank_bound import envelope,direct_reference
from compatibility import cover_bound
from enumeration import exhaustive_count
from mip_reference import solve
R=Path(__file__).resolve().parent/'results'
def main():
 records=[]
 for path in sorted((R/'fixtures').glob('*.npz')):
  z=np.load(path,allow_pickle=False);splits=np.cumsum(z['sizes'])[:-1];D=np.split(z['margins'],splits);U=np.split(z['upper_margins'],splits);b=int(z['budget']);L=z['lower']
  assert np.all(z['upper_margins']>=z['margins'])
  e=envelope(D,U,L,b,40);ref=direct_reference(D,U,L,b);g=cover_bound(D,U,b,120,80);en=exhaustive_count(D,U,b);mip=solve(U,L,b,1.)
  bound=min(len(L),math.floor(np.nextafter(e['upper_count'],np.inf)),g['count_upper'],en.get('rank_upper',len(L)+1)-1)
  # Independent state traversal when the exact finite lattice is small.
  count=1;coeff=[1]+[0]*b
  for size in z['sizes']:
   for j in range(b,0,-1):coeff[j]+=coeff[j-1]*(int(size)-1)
  states=sum(coeff);exact=None
  if states<=5000 and states*max(1,len(L))<=2_000_000:
   best=[0]
   def visit(i,cost,value):
    if i==len(D):best[0]=max(best[0],int((value>=0).sum()));return
    visit(i+1,cost,value+D[i][0])
    if cost<b:
     for row in D[i][1:]:visit(i+1,cost+1,value+row)
   visit(0,0,np.zeros(len(L)));exact=best[0];assert exact<=bound
   if mip.get('count_upper') is not None:assert exact<=mip['count_upper']+1e-5
   if ref.get('success'):assert exact<=ref['upper_count']+1e-8
  records.append({'fixture':path.name,'budget':b,'competitors':len(L),'finite_states':states,'independent_enumerated_count':exact,
   'proposed_count_upper':bound,'generic_lp':ref,'generic_mip':mip,'graph_edges':sum(x.get('incompatible',False) for x in g.get('checks',[]))})
 (R/'fixture_audit.json').write_text(json.dumps(records,indent=2));print('Audited',len(records),'real-query fixtures;',sum(x['independent_enumerated_count'] is not None for x in records),'independently enumerated')
if __name__=='__main__':main()
