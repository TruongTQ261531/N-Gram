"""Exact budgeted orthographic lattice oracle; established dynamic-programming primitives."""
import numpy as np
from numba import njit
@njit(cache=True)
def exact_path(u,e,cost,budget):
 n,q=u.shape
 dp=np.full((budget+1,q),-1e100)
 back=np.full((n,budget+1,q),-1,np.int16)
 for s in range(q):
  b=cost[0,s]
  if b<=budget:dp[b,s]=u[0,s]
 for i in range(1,n):
  nd=np.full((budget+1,q),-1e100)
  for b in range(budget+1):
   for s in range(q):
    cb=cost[i,s]
    if cb>b:continue
    for t in range(q):
     v=dp[b-cb,t]+e[i,t,s]+u[i,s]
     if v>nd[b,s]:nd[b,s]=v;back[i,b,s]=t
  dp=nd
 best=-1e100;bb=0;ss=0
 for b in range(budget+1):
  for s in range(q):
   if dp[b,s]>best:best=dp[b,s];bb=b;ss=s
 path=np.zeros(n,np.int16)
 for i in range(n-1,-1,-1):
  path[i]=ss;t=back[i,bb,ss];bb-=cost[i,ss];ss=t
 return best,path
@njit(cache=True)
def path_score(u,e,path):
 v=0.
 for i in range(len(path)):
  v+=u[i,path[i]]
  if i:v+=e[i,path[i-1],path[i]]
 return v
@njit(cache=True)
def greedy_path(u,e,cost,budget):
 n,q=u.shape;p=np.zeros(n,np.int16);spent=0
 for it in range(n*q):
  gain=1e-12;bi=-1;bs=-1
  for i in range(n):
   old=p[i]
   for s in range(q):
    if s==old or spent-cost[i,old]+cost[i,s]>budget:continue
    g=u[i,s]-u[i,old]
    if i:g+=e[i,p[i-1],s]-e[i,p[i-1],old]
    if i+1<n:g+=e[i+1,s,p[i+1]]-e[i+1,old,p[i+1]]
    if g>gain:gain=g;bi=i;bs=s
  if bi<0:break
  spent+=cost[bi,bs]-cost[bi,p[bi]];p[bi]=bs
 return path_score(u,e,p),p
@njit(cache=True)
def factor_upper(u,e,cost,budget):
 # Valid upper bound by relaxing shared states between factors. No greedy certificate.
 n,q=u.shape;edge=0.
 for i in range(1,n):
  mx=-1e100
  for t in range(q):
   if cost[i-1,t]>budget:continue
   for s in range(q):
    if cost[i,s]>budget:continue
    mx=max(mx,e[i,t,s])
  edge+=mx
 best=1e100
 for lam in [0.,.001,.003,.01,.03,.1,.3,1.,3.,10.]:
  val=lam*budget+edge
  for i in range(n):
   mx=-1e100
   for s in range(q):
    if cost[i,s]<=budget:mx=max(mx,u[i,s]-lam*cost[i,s])
   val+=mx
  best=min(best,val)
 return best
