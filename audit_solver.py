"""Measure seed-17 full-data ridge normal-equation residuals, not just toy tests."""
import os
for x in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[x]='1'
import json,pickle
import numpy as np,pandas as pd
from scipy import sparse
from study import RES,DATASETS,METHODS,load_data,matrices
from noise import augment
rows=[]
for ds in DATASETS:
 tr,_,_,enc,_=load_data(ds)
 with open(RES/(ds+'_prepared.pkl'),'rb') as f:c,w,r,enc=pickle.load(f)
 M=matrices(list(tr.text),c,w);y=enc.transform(tr.label);k=len(enc.classes_);n=len(y);Y=np.eye(k)[y];sw=(n/(k*np.bincount(y)))[y]
 A=sparse.vstack([M['char'],M['folded'],c.transform([augment(s,17) for s in tr.text])],format='csr');Z=np.tile(Y,(3,1));aws=np.tile(sw/3,3)
 for m in METHODS:
  with open(RES/(ds+'_'+m+'_seed17.pkl'),'rb') as f:b=pickle.load(f)
  model=b['model'];cf=b['config']
  if m=='svm':
   rows.append(dict(dataset=ds,method=m,iterations=str(model.n_iter_),relative_normal_equation_residual=None,hit_max_iter=bool(model.n_iter_>=3000)));continue
  if m in ['aug','uniform','capc','shuffled']:
   X=A;T=Z;ww=aws
   if m!='aug':
    rel=np.ones(n) if m=='uniform' else r.copy()
    if m=='shuffled':np.random.default_rng(17).shuffle(rel)
    X=sparse.vstack([A,M['char']-M['folded']],format='csr');T=np.vstack([Z,np.zeros((n,k))]);ww=np.r_[aws,cf['lam']*sw*rel]
  else:X=M[m];T=Y;ww=sw
  coef=model.coef_.T;rhs=X.T@(ww[:,None]*T);g=X.T@(ww[:,None]*(X@coef-T))+cf['alpha']*coef
  residual=float(np.linalg.norm(g)/max(np.linalg.norm(rhs),1e-30));assert np.isfinite(residual)
  rows.append(dict(dataset=ds,method=m,iterations=json.dumps(model.n_iter_.tolist()),relative_normal_equation_residual=residual,hit_max_iter=bool(np.max(model.n_iter_)>=500)))
pd.DataFrame(rows).to_csv(RES/'solver_audit.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
