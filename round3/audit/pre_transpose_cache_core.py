"""Fixed character-BM25 and coupled query-perturbation ranking certificates.

Exactness statements are for the finite token-variant set and stored index weights.
No new ranking model, semantic label preservation, or Q1 novelty is assumed.
"""
import os
for _key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
 os.environ[_key]='1'
from pathlib import Path
from collections import Counter
import itertools,math,pickle,time,unicodedata
import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import CountVectorizer

ROOT=Path(__file__).resolve().parent
EPS=np.finfo(np.float64).eps

def normalize(text):return ' '.join(unicodedata.normalize('NFC',str(text)).casefold().split())

def grams(text):
 for token in normalize(text).split():
  t=' '+token+' '
  for n in (3,4,5):
   for i in range(len(t)-n+1):yield t[i:i+n]

_coords={c:(j+off,i) for i,(row,off) in enumerate([('qwertyuiop',0),('asdfghjkl',.3),('zxcvbnm',.7)]) for j,c in enumerate(row)}
NEIGHBORS={c:sorted(k for k,(x,y) in _coords.items() if k!=c and (x-a)**2+(y-b)**2<=1.6**2) for c,(a,b) in _coords.items()}

def variants(token):
 """Raw, all single deletions, adjacent swaps, repeats, QWERTY neighbors.
 One chosen original token may undergo at most one operation. Cost is changed
 original tokens, NOT arbitrary Levenshtein/codepoint distance.
 """
 found={token:None}
 for i,c in enumerate(token):
  found.setdefault(token[:i]+token[i+1:],{'op':'delete','pos':i})
  found.setdefault(token[:i]+c+token[i:],{'op':'repeat','pos':i})
  for z in NEIGHBORS.get(c,[]):found.setdefault(token[:i]+z+token[i+1:],{'op':'keyboard','pos':i,'char':z})
  if i+1<len(token):found.setdefault(token[:i]+token[i+1]+c+token[i+2:],{'op':'swap','pos':i})
 forms=[token]+sorted(x for x in found if x!=token)
 return forms,[found[x] for x in forms]

class Index:
 def __init__(self,texts,ids,kind='char'):
  self.ids=np.array(list(map(str,ids)));self.kind=kind
  self.v=CountVectorizer(analyzer=grams,dtype=np.float64) if kind=='char' else CountVectorizer(
    analyzer='word',lowercase=True,dtype=np.float64,token_pattern=r'(?u)\b\w+\b')
  x=self.v.fit_transform(texts).tocsr();self.n=x.shape[0]
  length=np.asarray(x.sum(1)).ravel();avg=float(length.mean())
  df=np.bincount(x.indices,minlength=x.shape[1]);idf=np.log1p((self.n-df+.5)/(df+.5))
  denom=1.2*(1-.75+.75*length/max(avg,1e-30))
  x.data=x.data*2.2/(x.data+np.repeat(denom,np.diff(x.indptr)))*idf[x.indices]
  self.W=x;self.idf=idf

 def score(self,text):return np.asarray((self.v.transform([text])@self.W.T).toarray()).ravel()

 def query(self,text):
  assert self.kind=='char'
  tokens=normalize(text).split()
  forms_ops=[variants(t) for t in tokens]
  return Query(self,tokens,forms_ops)

 def save(self,path):
  with open(path,'wb') as f:pickle.dump(self,f,protocol=5)

 @classmethod
 def load(cls,path):
  with open(path,'rb') as f:return pickle.load(f)

class Query:
 def __init__(self,index,tokens,forms_ops):
  self.index=index;self.tokens=tokens;self.forms=[x[0] for x in forms_ops];self.ops=[x[1] for x in forms_ops]
  self.features=[index.v.transform(f).tocsr() for f in self.forms]
  self._scores=None

 def all_scores(self):
  if self._scores is None:self._scores=[(x@self.index.W.T).toarray() for x in self.features]
  return self._scores

 def raw(self):
  return self.index.score(' '.join(self.tokens))

 def rankings(self,scores=None):
  if scores is None:scores=self.raw()
  return np.lexsort((self.index.ids,-scores))

 def text(self,choices):return ' '.join(self.forms[i][int(a)] for i,a in enumerate(choices))

 def trace(self,choices):return [{'token':i,**self.ops[i][int(a)]} for i,a in enumerate(choices) if a]

def outward_scores(scores,features):
 """Conservative dot-product intervals for exact stored nonnegative weights.
 gamma uses eps=2u and extra operations; assumes finite IEEE float64 arithmetic.
 Sparse summation order does not matter for the conventional forward-error bound.
 """
 lo=[];hi=[]
 for f,a in zip(scores,features):
  p=np.diff(a.indptr).astype(float)
  m=2*p+2;gamma=m*EPS/(1-m*EPS)
  e=np.nextafter((gamma/(1-gamma))[:,None]*np.abs(f)+m[:,None]*np.nextafter(0.,1.),np.inf)
  lo.append(np.nextafter(f-e,-np.inf));hi.append(np.nextafter(f+e,np.inf))
 return lo,hi

def top_gain_sum(gains,bmax,up=False):
 if not gains:return np.zeros((bmax+1,0))
 g=np.maximum(np.stack(gains),0.)
 g=np.sort(g,axis=0)[::-1]
 out=np.zeros((bmax+1,g.shape[1]))
 for b in range(1,bmax+1):
  val=out[b-1]+(g[b-1] if b<=len(g) else 0.)
  out[b]=np.nextafter(val,np.inf) if up else val
 return out

def independent(scores,lo,hi,bmax):
 n=scores[0].shape[1];upper=np.zeros(n);lower=np.zeros(n);ug=[];lg=[]
 for l,h in zip(lo,hi):
  upper=np.nextafter(upper+h[0],np.inf);lower=np.nextafter(lower+l[0],-np.inf)
  ug.append(np.nextafter(h.max(0)-l[0],np.inf))
  lg.append(np.nextafter(h[0]-l.min(0),np.inf))
 U=top_gain_sum(ug,bmax,True);D=top_gain_sum(lg,bmax,True)
 return np.nextafter(upper[None,:]+U,np.inf),np.nextafter(lower[None,:]-D,-np.inf)

def coupled_for_ref(scores,lo,hi,ref,candidates,bmax):
 cand=np.asarray(candidates,dtype=int);base=np.zeros(len(cand));base_up=base.copy();gains=[];gup=[];states=[]
 for f,l,h in zip(scores,lo,hi):
  d=f[:,cand]-f[:,ref,None];best=np.argmax(d,axis=0)
  base+=d[0];gains.append(d[best,np.arange(len(cand))]-d[0]);states.append(best)
  rawu=np.nextafter(h[0,cand]-l[0,ref],np.inf)
  rawl=np.nextafter(l[0,cand]-h[0,ref],-np.inf)
  best_u=np.max(np.nextafter(h[:,cand]-l[:,ref,None],np.inf),axis=0)
  base_up=np.nextafter(base_up+rawu,np.inf);gup.append(np.nextafter(best_u-rawl,np.inf))
 return base[None,:]+top_gain_sum(gains,bmax),np.nextafter(base_up[None,:]+top_gain_sum(gup,bmax,True),np.inf),gains,states

def witness(gains,states,column,budget):
 choices=np.zeros(len(gains),dtype=int)
 order=sorted(range(len(gains)),key=lambda t:(-gains[t][column],t))
 for t in order[:budget]:
  if gains[t][column]>0:choices[t]=states[t][column]
 return choices

def certify(scores,features,ranking,k=1,bmax=3,prune=True):
 """Return strict-top-k certificates. Ties/numerical uncertainty are not certified.
 All corpus outsiders are bounded or evaluated; there is no hidden top-100 filter.
 """
 n=scores[0].shape[1];inside=np.asarray(ranking[:k]);outside=np.asarray(ranking[k:])
 lo,hi=outward_scores(scores,features);U,L=independent(scores,lo,hi,bmax)
 loose=np.array([U[b,outside].max(initial=-np.inf)<L[b,inside].min(initial=np.inf) for b in range(bmax+1)])
 upper=np.full(bmax+1,-np.inf);point=np.full(bmax+1,-np.inf);best=[None]*(bmax+1);pairs=0
 for ref in inside:
  if prune:
   safe=np.nextafter(U[bmax,outside]-L[bmax,ref],np.inf)
   keep=safe>=0
   for b in range(bmax+1):upper[b]=max(upper[b],np.max(np.nextafter(U[b,outside[~keep]]-L[b,ref],np.inf),initial=-np.inf))
   candidates=outside[keep]
  else:candidates=outside
  pairs+=len(candidates)
  if not len(candidates):continue
  m,up,g,st=coupled_for_ref(scores,lo,hi,int(ref),candidates,bmax)
  upper=np.maximum(upper,up.max(1))
  for b in range(bmax+1):
   j=int(np.argmax(m[b]))
   if m[b,j]>point[b]:
    point[b]=float(m[b,j]);best[b]={'inside':int(ref),'outside':int(candidates[j]),'choices':witness(g,st,j,b).tolist()}
 return {'cert':upper<0,'loose':loose,'upper':upper,'point':point,'witness':best,'pairs':pairs,'all_pairs':len(inside)*len(outside)}

def brute_margin(scores,inside,budget):
 n=scores[0].shape[1];outside=[j for j in range(n) if j not in inside];value=-np.inf
 for choices in itertools.product(*[range(len(x)) for x in scores]):
  if sum(a!=0 for a in choices)>budget:continue
  total=sum(f[a] for f,a in zip(scores,choices))
  value=max(value,max((total[j]-total[i] for i in inside for j in outside),default=-np.inf))
 return value

def metrics(ranking,ids,relevances,k=10):
 rel=np.array([float(relevances.get(str(ids[j]),0)) for j in ranking[:k]])
 gains=np.power(2.,rel)-1.;discount=1/np.log2(np.arange(2,len(rel)+2))
 ideal=np.sort(list(relevances.values()))[::-1][:k]
 idcg=sum((2**v-1)/math.log2(i+2) for i,v in enumerate(ideal))
 hit=sum(v>0 for v in rel);positive=sum(v>0 for v in relevances.values())
 return {'ndcg10':float(gains@discount/idcg) if idcg else 0.,'recall10':hit/positive if positive else 0.,'hit1':bool(len(rel) and rel[0]>0)}
