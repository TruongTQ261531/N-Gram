import os
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
import sys,unicodedata as ud,time,json,pickle
from pathlib import Path
from dataclasses import dataclass
import numpy as np,pandas as pd
from scipy import sparse
from scipy.optimize import minimize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.utils import murmurhash3_32
from sklearn.metrics import f1_score,accuracy_score
from sklearn.model_selection import train_test_split
LEGACY=Path(__file__).resolve().parents[1]
if (LEGACY/'ngram-study'/'noise.py').exists():LEGACY=LEGACY/'ngram-study'
sys.path.insert(0,str(LEGACY))
from noise import normalize,fold
from lattice import exact_path,greedy_path,factor_upper,path_score
ROOT=Path(__file__).resolve().parent
RES=ROOT/'results';RES.mkdir(exist_ok=True)
TONE='\u0300\u0301\u0303\u0309\u0323'
def tonefold(s):return ud.normalize('NFC',''.join(c for c in ud.normalize('NFD',s) if c not in TONE))
def variants(t):
 forms=[s for s in dict.fromkeys([t,tonefold(t),fold(t)]) if len(s)==len(t)]
 assert forms and forms[0]==t
 return forms
@dataclass
class Doc:
 ids: np.ndarray
 costs: np.ndarray
 edges: np.ndarray
 canon: np.ndarray
 cedge: np.ndarray
 ci: np.ndarray
 cv: np.ndarray
 tokens: list
 row_id: int
class Encoder:
 def __init__(self,train_texts,max_features=12000,bins=8192):
  self.bins=bins;tt=set()
  for text in train_texts:
   for t in normalize(text).split()[:128]:tt.update(variants(t))
  self.v=TfidfVectorizer(analyzer='char',ngram_range=(2,5),max_features=max_features,sublinear_tf=True,lowercase=False,dtype=np.float64)
  self.v.fit(sorted(tt));self.f=len(self.v.vocabulary_);self.d=2*self.f+2*bins+1
  self.words=[];self.index={}
  self.add(sorted(tt))
 def add(self,words):
  new=[]
  for t in words:
   if t not in self.index:self.index[t]=len(self.words);self.words.append(t);new.append(t)
  if new:
   a=self.v.transform(new)
   self.V=a if not hasattr(self,'V') else sparse.vstack([self.V,a],format='csr')
 def h(self,a,b):
  # Stable string-based hashing independent of vocabulary/test corpus.
  return ((int(murmurhash3_32(a,positive=True))*1000003)^int(murmurhash3_32(b,positive=True)))%self.bins
 def encode(self,text,row_id=0):
  toks=normalize(text).split()[:128];assert toks
  vs=[variants(t) for t in toks];self.add([w for v in vs for w in v]);self.add([fold(t) for t in toks]);n=len(toks)
  ids=np.zeros((n,3),np.int32);cost=np.full((n,3),100000,np.int32)
  for i,(t,forms) in enumerate(zip(toks,vs)):
   for j,s in enumerate(forms):ids[i,j]=self.index[s];cost[i,j]=sum(a!=b for a,b in zip(t,s))
  edge=np.zeros((n,3,3),np.int32);canon=np.array([self.index[fold(t)] for t in toks],np.int32);ce=np.zeros(n,np.int32)
  for i in range(1,n):
   ce[i]=self.h(fold(toks[i-1]),fold(toks[i]))
   for a in range(len(vs[i-1])):
    for b in range(len(vs[i])):edge[i,a,b]=self.h(vs[i-1][a],vs[i][b])
  z=sparse.csr_matrix((np.ones(n),(np.zeros(n,dtype=int),canon)),shape=(1,len(self.words)))@self.V
  hi,hc=np.unique(ce[1:],return_counts=True)
  ci=np.r_[z.indices+self.f,hi+2*self.f+self.bins,self.d-1].astype(np.int32)
  cv=np.r_[z.data/np.sqrt(n),hc/np.sqrt(n),1.]
  return Doc(ids,cost,edge,canon,ce,ci,cv,toks,int(row_id))
 def features(self,docs,paths=None):
  inds=[];vals=[];ptr=[0]
  for j,d in enumerate(docs):
   n=len(d.ids);path=np.zeros(n,np.int16) if paths is None else paths[j]
   ids=d.ids[np.arange(n),path]
   z=sparse.csr_matrix((np.ones(n),(np.zeros(n,dtype=int),ids)),shape=(1,len(self.words)))@self.V
   ed=d.edges[np.arange(1,n),path[:-1],path[1:]];hi,hc=np.unique(ed,return_counts=True)
   ii=np.r_[z.indices,hi+2*self.f,d.ci];vv=np.r_[z.data/np.sqrt(n),hc/np.sqrt(n),d.cv]
   inds.extend(ii);vals.extend(vv);ptr.append(len(inds))
  m=sparse.csr_matrix((vals,inds,ptr),shape=(len(docs),self.d));m.sum_duplicates();return m
 def tables(self,W):return self.V@W[:self.f],self.V@W[self.f:2*self.f]
 def potentials(self,W,d,tables):
  r,c=tables;n=len(d.ids);scale=1/np.sqrt(n)
  u=(r[d.ids]+c[d.canon][:,None,:])*scale
  e=(W[2*self.f:2*self.f+self.bins][d.edges]+W[2*self.f+self.bins:2*self.f+2*self.bins][d.cedge][:,None,None,:])*scale
  e[0]=0
  return u,e
 def mask(self,method):
  m=np.ones(self.d)
  if method=='canonical':m[:self.f]=0;m[2*self.f:2*self.f+self.bins]=0
  if method=='unary':m[2*self.f:2*self.f+2*self.bins]=0
  return m

def class_weight(y):return len(y)/(len(np.unique(y))*np.bincount(y))
def score_metrics(y,p,k):return {'macro_f1':float(f1_score(y,p,labels=np.arange(k),average='macro',zero_division=0)),'accuracy':float(np.mean(y==p))}

def train(enc,docs,y,k,alpha,eta,seed,method,rounds=6,maxiter=50,budget=3):
 t0=time.perf_counter();X=enc.features(docs);n=len(docs);cw=class_weight(y)[y];den=n*(k-1);rng=np.random.default_rng(seed)
 idx=np.repeat(np.arange(n),k-1);comp=np.array([c for yi in y for c in range(k) if c!=yi]);yy=y[idx];H=len(idx)
 mask=enc.mask(method);W=rng.normal(0,1e-5,(enc.d,k))*mask[:,None];logs=[]
 # Each block has exactly one witness per (document, competing class).
 V=X[idx];blocks=1
 effective_eta=0. if method in ['clean','canonical'] else eta
 if method=='random':
  ps=[]
  for d in docs:
   p=np.zeros(len(d.ids),np.int16);order=rng.permutation(len(p));spent=0
   for i in order:
    choices=np.where((d.costs[i]>0)&(d.costs[i]<=budget-spent))[0]
    if len(choices) and rng.random()<.5:p[i]=rng.choice(choices);spent+=d.costs[i,p[i]]
   ps.append(p)
  V=sparse.vstack([V,enc.features(docs,ps)[idx]],format='csr');blocks=2
 def obj(theta):
  W0=theta.reshape(enc.d,k)*mask[:,None]
  S=X@W0;A=np.maximum(0,1+S-S[np.arange(n),y,None]);A[np.arange(n),y]=0
  clean=float(np.sum(cw[:,None]*A*A)/den);G=2*cw[:,None]*A/den;G[np.arange(n),y]=-G.sum(1)
  grad=(1-effective_eta)*(X.T@G);value=(1-effective_eta)*clean
  if effective_eta:
   SS=V@W0;row=np.arange(len(idx)*blocks);cc=np.tile(comp,blocks);yt=np.tile(yy,blocks)
   a=(1+SS[row,cc]-SS[row,yt]).reshape(blocks,H);j=a.argmax(0);v=np.maximum(0,a[j,np.arange(H)]);active=j*H+np.arange(H)
   value+=effective_eta*float(np.sum(cw[idx]*v*v)/den)
   DD=np.zeros((H,k));scale=2*effective_eta*cw[idx]*v/den;DD[np.arange(H),comp]=scale;DD[np.arange(H),yy]-=scale
   grad+=V[active].T@DD
  value+=alpha*.5*np.sum(W0*W0);grad=(grad+alpha*W0)*mask[:,None]
  return float(value),grad.ravel()
 nround=1 if method in ['clean','canonical','random'] else rounds
 for r in range(nround):
  fit=minimize(obj,W.ravel(),method='L-BFGS-B',jac=True,options={'maxiter':maxiter,'ftol':1e-9,'gtol':1e-5,'maxcor':8})
  W=fit.x.reshape(enc.d,k)*mask[:,None]
  rec={'round':r,'restricted_objective':float(fit.fun),'optimizer_success':bool(fit.success),'message':str(fit.message),'nit':int(fit.nit),'gradient_norm':float(np.linalg.norm(fit.jac)),'witness_blocks':blocks};logs.append(rec)
  if method in ['clean','canonical','random']:break
  tab=enc.tables(W);paths=[];oracle=[]
  for di,c,yi in zip(idx,comp,yy):
   d=docs[di];u,e=enc.potentials(W,d,tab);fn=greedy_path if method=='greedy' else exact_path
   val,path=fn(np.ascontiguousarray(u[:,:,c]-u[:,:,yi]),np.ascontiguousarray(e[:,:,:,c]-e[:,:,:,yi]),d.costs,budget)
   paths.append(path);oracle.append(1+val+W[-1,c]-W[-1,yi])
  oracle=np.maximum(0,np.array(oracle));true_loss=float(np.sum(cw[idx]*oracle**2)/den)
  S=X@W;A=np.maximum(0,1+S-S[np.arange(n),y,None]);A[np.arange(n),y]=0
  true_obj=alpha*.5*np.sum(W*W)+(1-effective_eta)*np.sum(cw[:,None]*A*A)/den+effective_eta*true_loss
  rec['separation_gap']=float(max(0,true_obj-fit.fun));rec['separation_is_exact']=method!='greedy'
  if r+1<nround:
   VV=enc.features([docs[i] for i in idx],paths);V=sparse.vstack([V,VV],format='csr');blocks+=1
 return W,{'seconds':time.perf_counter()-t0,'rounds':logs,'alpha':alpha,'eta':effective_eta,'seed':seed,'method':method,'budget':budget,'maxiter':maxiter}

def evaluate(enc,docs,y,W,budgets=(0,1,2,3,5),diagnose=True):
 k=W.shape[1];n=len(docs);pred=(enc.features(docs)@W).argmax(1);tables=enc.tables(W)
 margins=np.full((len(budgets),n,k),-1e100);loose=np.zeros((len(budgets),n),bool);greedy=np.zeros((len(budgets),n),bool)
 t=time.perf_counter()
 for i,d in enumerate(docs):
  u,e=enc.potentials(W,d,tables);yi=y[i]
  for bi,b in enumerate(budgets):
   ub=[];gb=[]
   for c in range(k):
    if c==yi:continue
    um=np.ascontiguousarray(u[:,:,c]-u[:,:,yi]);em=np.ascontiguousarray(e[:,:,:,c]-e[:,:,:,yi]);bias=W[-1,c]-W[-1,yi]
    v,path=exact_path(um,em,d.costs,int(b));margins[bi,i,c]=v+bias
    if diagnose:
     ub.append(factor_upper(um,em,d.costs,int(b))+bias);gb.append(greedy_path(um,em,d.costs,int(b))[0]+bias)
   if diagnose:loose[bi,i]=max(ub)<-1e-9;greedy[bi,i]=max(gb)<-1e-9
 cert=margins.max(2)<-1e-9
 assert np.all(cert==np.minimum.accumulate(cert,axis=0)),'robustness must decrease with budget'
 assert np.all(~loose|cert),'unsound factor certificate'
 if diagnose:assert np.all(~cert|greedy),'greedy must not be stronger than exact attack'
 return {'pred':pred,'cert':cert,'margins':margins,'loose_cert':loose,'greedy_survives':greedy,'seconds':time.perf_counter()-t}
