"""Safe index-level screening before dense alternative-score materialization."""
import numpy as np
from scipy import sparse
from core import EPS,outward_scores,top_gain_sum
from rank_bound import retention

def dot_upper(X,W):
 v=(X@W).toarray();p=np.diff(X.indptr).astype(float)
 m=2*p+2;gamma=m*EPS/(1-m*EPS)
 e=np.nextafter((gamma/(1-gamma))[:,None]*np.abs(v)+m[:,None]*np.nextafter(0.,1.),np.inf)
 return np.nextafter(v+e,np.inf)

def coarse_candidates(query,ranking,bmax=3):
 """Every discarded document is below the reference for ALL allowed queries."""
 I=query.index;ref=int(ranking[0]);A=query.features
 # Scores for just one document are cheap and preserve per-token coupling.
 Wref=I.W[ref].T.tocsr();R=[(a@Wref).toarray() for a in A]
 lo,hi=outward_scores(R,A)
 raw_lower=0.;drops=[]
 for l,h in zip(lo,hi):
  raw_lower=np.nextafter(raw_lower+l[0,0],-np.inf)
  drops.append(np.array([np.nextafter(h[0,0]-l[:,0].min(),np.inf)]))
 ref_lower=np.nextafter(raw_lower-top_gain_sum(drops,bmax,True)[:,0],-np.inf)
 raw=sparse.csr_matrix(sum((a[0] for a in A)))
 delta=sparse.vstack([(a.max(axis=0).tocsr()-a[0]).tocsr() for a in A],format='csr')
 cols=np.unique(np.r_[raw.indices,delta.indices]);changes=delta[:,cols].toarray()
 changes=np.sort(np.maximum(changes,0),axis=0)[::-1]
 base=raw[:,cols].toarray().ravel();counts=[]
 for b in range(bmax+1):counts.append(base+changes[:b].sum(0))
 X=sparse.csr_matrix((np.concatenate(counts),(np.repeat(np.arange(bmax+1),len(cols)),np.tile(cols,bmax+1))),shape=(bmax+1,I.W.shape[1]))
 upper=dot_upper(X,I.transpose())
 keep=[np.flatnonzero(upper[b]>=ref_lower[b]) for b in range(bmax+1)]
 # A zero reference score implies worst-tie rank N for nonnegative BM25.
 assert I.W.data.min(initial=1.)>1e-250
 can_zero=all(np.any(f[:,0]==0.) for f in R)
 choices=[int(np.flatnonzero(f[:,0]==0.)[0]) if np.any(f[:,0]==0.) else 0 for f in R]
 cost=sum(a!=0 for a in choices)
 zero=[bool(can_zero and cost<=b) for b in range(bmax+1)]
 return {'ref':ref,'reference_lower':ref_lower,'upper_scores':upper,'keep':keep,'zero':zero,'zero_choices':choices}

def screened_retention(query,ranking,bmax=3,max_iterations=40):
 I=query.index;coarse=coarse_candidates(query,ranking,bmax)
 active=[b for b in range(1,bmax+1) if not coarse['zero'][b]]
 if active:
  bactive=max(active);docs=np.array([coarse['ref']]+sorted(set(coarse['keep'][bactive])-{coarse['ref']}),dtype=int)
  W=I.W[docs].T.tocsr();F=[(a@W).toarray() for a in query.features]
  r=retention(F,query.features,np.arange(len(docs)),bactive,max_iterations)
 else:docs=np.array([coarse['ref']]);F=None;r=[]
 result=[]
 for b in range(1,bmax+1):
  if coarse['zero'][b]:
   e={'budget':b,'reference':coarse['ref'],'candidate_indices':[],'pairwise_upper_count':I.n-1,
    'pairwise_rank_upper':I.n,'rank_upper':I.n,'upper_count':float(I.n-1),'strict_top1_certified':False,
    'zero_reference_shortcut':True,'choices':coarse['zero_choices'],'weights':[],'iterations':0,'envelope_gap':0.,'history':[],
    'observed_strict_count':None,'max_pair_margin':None,'max_pair_upper':None}
  else:
   e=r[b-1];e['candidate_indices']=docs[np.asarray(e['candidate_indices'],dtype=int)].tolist();e['reference']=coarse['ref'];e['zero_reference_shortcut']=False
  e['coarse_documents']=int(len(coarse['keep'][b]));e['materialized_documents']=int(len(docs)) if active else 0
  result.append(e)
 return result,coarse,docs,F
