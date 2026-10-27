"""A posteriori strong-convexity bound for exported seed-17 BOLT models."""
import json,pickle
import numpy as np
from core import RES,train,class_weight
from run import DS
from lattice import exact_path
rows=[]
for ds in DS:
 with open(RES/(ds+'_bolt_seed17.pkl'),'rb') as f:en,W=pickle.load(f)
 with open(RES/(ds+'_prepared.pkl'),'rb') as f:_,td,y,_,_,le,_=pickle.load(f)
 cf=json.loads((RES/'selected.json').read_text())[ds]['bolt'];alpha=cf['alpha'];eta=cf['eta'];n=len(td);k=len(le.classes_);den=n*(k-1);cw=class_weight(y)[y]
 X=en.features(td);S=X@W;A=np.maximum(0,1+S-S[np.arange(n),y,None]);A[np.arange(n),y]=0
 G=2*(1-eta)*cw[:,None]*A/den;G[np.arange(n),y]=-G.sum(1);grad=X.T@G+alpha*W
 tab=en.tables(W);docs=[];paths=[];comp=[];truth=[];dd=[];values=[]
 for i,d in enumerate(td):
  u,e=en.potentials(W,d,tab)
  for c in range(k):
   if c==y[i]:continue
   val,path=exact_path(np.ascontiguousarray(u[:,:,c]-u[:,:,y[i]]),np.ascontiguousarray(e[:,:,:,c]-e[:,:,:,y[i]]),d.costs,3)
   values.append(max(0,1+val+W[-1,c]-W[-1,y[i]]));docs.append(d);paths.append(path);comp.append(c);truth.append(y[i]);dd.append(i)
 values=np.array(values);dd=np.array(dd);V=en.features(docs,paths);D=np.zeros((len(paths),k));scale=2*eta*cw[dd]*values/den;D[np.arange(len(paths)),comp]=scale;D[np.arange(len(paths)),truth]-=scale;grad+=V.T@D
 norm=float(np.linalg.norm(grad));obj=alpha*.5*np.sum(W*W)+(1-eta)*np.sum(cw[:,None]*A*A)/den+eta*np.sum(cw[dd]*values**2)/den
 rows.append({'dataset':ds,'full_objective':float(obj),'full_subgradient_norm':norm,'strong_convexity_gap_upper':norm**2/(2*alpha),'meaning':'F(W)-F* <= ||g||^2/(2 alpha), using one exact-max witness subgradient. Loose at nonsmooth ties. No claim of a small gap unless the value supports it.'})
(RES/'optimization_audit.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
