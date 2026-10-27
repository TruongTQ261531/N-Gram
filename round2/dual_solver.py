"""Primal-dual coordinate solver audit for the same BOLT convex objective.
Standard squared-hinge Fenchel dual / coordinate ascent, not a new general solver claim.
"""
import numpy as np
from scipy import sparse
from numba import njit
from lattice import exact_path
from core import class_weight
@njit(cache=True)
def coordinate_epoch(indptr,indices,data,comp,truth,group,lam,alpha,a,A,W,order):
 pgmax=0.
 for ii in order:
  c=comp[ii];y=truth[ii];g=group[ii];dot=0.;norm=0.
  for j in range(indptr[ii],indptr[ii+1]):
   v=data[j];f=indices[j];dot+=v*(W[f,c]-W[f,y]);norm+=v*v
  grad=1+dot-A[g]/(2*lam[g]);pg=grad if a[ii]>0 else max(0.,grad);pgmax=max(pgmax,abs(pg))
  delta=max(-a[ii],grad/(2*norm/alpha+1/(2*lam[g])))
  a[ii]+=delta;A[g]+=delta
  for j in range(indptr[ii],indptr[ii+1]):
   dv=delta*data[j]/alpha;f=indices[j];W[f,c]-=dv;W[f,y]+=dv
 return pgmax

def dual_value(a,A,W,lam,alpha):return float(a.sum()-.5*alpha*np.sum(W*W)-np.sum(A*A/(4*lam)))
def optimize_pool(X,comp,truth,group,lam,alpha,a,A,W,epochs=50,seed=17):
 rng=np.random.default_rng(seed);hist=[]
 for ep in range(epochs):
  pg=coordinate_epoch(X.indptr,X.indices,X.data,comp,truth,group,lam,alpha,a,A,W,rng.permutation(len(a)))
  hist.append(dual_value(a,A,W,lam,alpha))
  if ep and hist[-1]+1e-8<hist[-2]:raise AssertionError('dual must be monotone')
  if pg<1e-9:break
 return a,A,W,hist

def fit_dual(enc,docs,y,k,alpha,eta,seed,max_outer=10,epochs=40,budget=3,gap_tol=1e-4):
 assert alpha>0 and 0<eta<1
 n=len(y);H=n*(k-1);den=n*(k-1);idx=np.repeat(np.arange(n),k-1);cs=np.array([c for yi in y for c in range(k) if c!=yi],np.int32);ys=y[idx].astype(np.int32);cw=class_weight(y)[y]
 lam=np.r_[(1-eta)*cw[idx]/den,eta*cw[idx]/den]
 clean=enc.features(docs);X=sparse.vstack([clean[idx],clean[idx]],format='csr');comp=np.tile(cs,2);truth=np.tile(ys,2);group=np.arange(2*H,dtype=np.int32)
 a=np.zeros(2*H);A=np.zeros(2*H);W=np.zeros((enc.d,k));seen=[{np.zeros(len(docs[i].ids),np.int16).tobytes()} for i in idx];logs=[]
 for outer in range(max_outer):
  a,A,W,dh=optimize_pool(X,comp,truth,group,lam,alpha,a,A,W,epochs,seed+outer)
  scores=clean@W;cl=np.maximum(0,1+scores-scores[np.arange(n),y,None]);cl[np.arange(n),y]=0
  tab=enc.tables(W);paths=[];vv=[];new=[]
  for h,(i,c,yi) in enumerate(zip(idx,cs,ys)):
   d=docs[i];u,e=enc.potentials(W,d,tab);v,p=exact_path(np.ascontiguousarray(u[:,:,c]-u[:,:,yi]),np.ascontiguousarray(e[:,:,:,c]-e[:,:,:,yi]),d.costs,budget)
   vv.append(max(0,1+v+W[-1,c]-W[-1,yi]));key=p.tobytes()
   if key not in seen[h]:seen[h].add(key);new.append(h);paths.append(p)
  vv=np.array(vv);primal=.5*alpha*np.sum(W*W)+(1-eta)*np.sum(cw[:,None]*cl*cl)/den+eta*np.sum(cw[idx]*vv*vv)/den
  dual=dual_value(a,A,W,lam,alpha);gap=float(primal-dual);assert gap>=-1e-7
  logs.append({'outer':outer,'primal':float(primal),'dual':dual,'gap':gap,'witness_rows':len(a),'new_witnesses':len(new),'coordinate_epochs':len(dh)})
  if gap<=gap_tol:break
  if new:
   V=enc.features([docs[idx[h]] for h in new],paths);X=sparse.vstack([X,V],format='csr');comp=np.r_[comp,cs[new]].astype(np.int32);truth=np.r_[truth,ys[new]].astype(np.int32);group=np.r_[group,np.array(new)+H].astype(np.int32);a=np.r_[a,np.zeros(len(new))]
 return W,logs
