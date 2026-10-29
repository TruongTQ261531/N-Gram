"""Certified retention via a shared-query affine-envelope bound.

The counting envelope, LP duality and cutting-plane machinery are established.
This is a candidate specialization, not a verified globally novel algorithm.
"""
import numpy as np
import time
from scipy import sparse
from scipy.optimize import linprog
from core import EPS,outward_scores,coupled_for_ref,top_gain_sum

def ranges(scores,lo,hi,ref,candidates,bmax):
 point,U,_,_=coupled_for_ref(scores,lo,hi,ref,candidates,bmax)
 c=np.asarray(candidates);base=np.zeros(len(c));drop=[]
 for l,h in zip(lo,hi):
  rawl=np.nextafter(l[0,c]-h[0,ref],-np.inf)
  rawu=np.nextafter(h[0,c]-l[0,ref],np.inf)
  bestl=np.min(np.nextafter(l[:,c]-h[:,ref,None],-np.inf),axis=0)
  base=np.nextafter(base+rawl,-np.inf);drop.append(np.nextafter(rawu-bestl,np.inf))
 L=np.nextafter(base[None,:]-top_gain_sum(drop,bmax,True),-np.inf)
 return point,L,U

def support(D,Du,w,budget):
 """Exact point support/witness, outward-rounded upper support."""
 raw=0.;gain=[];state=[];point_values=[];upper_values=[]
 for d,u in zip(D,Du):
  v=d@w;arg=int(v.argmax());raw+=v[0];gain.append(float(v[arg]-v[0]));state.append(arg);point_values.append(v)
  m=2*len(w)+2;gamma=m*EPS/(1-m*EPS)
  z=u@w;absolute=np.abs(u)@w
  err=np.nextafter(gamma*absolute/(1-gamma)+m*np.nextafter(0.,1.),np.inf)
  upper_values.append(np.nextafter(z+err,np.inf))
 choices=np.zeros(len(D),dtype=int)
 for t in sorted(range(len(D)),key=lambda i:(-gain[i],i))[:budget]:
  if gain[t]>0:choices[t]=state[t]
 margin=sum(d[a] for d,a in zip(D,choices))
 dp=np.zeros(budget+1)
 for u in upper_values:
  new=np.nextafter(dp+u[0],np.inf)
  if len(u)>1:
   for b in range(1,budget+1):new[b]=max(new[b],np.nextafter(dp[b-1]+u[1:].max(),np.inf))
  dp=new
 return float(sum(v[a] for v,a in zip(point_values,choices))),float(dp[-1]),choices,margin

def envelope(D,Du,lower,budget,max_iterations=40,tolerance=1e-6):
 """Each feasible weight vector independently gives a valid upper count.
 The master LP objective is only a lower bound on the best envelope, not a
 certified upper bound on adversarial rank. Never report it as a certificate.
 """
 m=len(lower)
 if not m:return {'upper_count':0.,'weights':[],'iterations':0,'master_lower':0.,'envelope_gap':0.,'history':[],'choices':[0]*len(D),'observed_strict_count':0}
 lower=np.minimum(np.asarray(lower),-1e-8)
 caps=np.nextafter(1/(-lower),0.)
 cuts=[sum(d[0] for d in D)];best=float(m);bestw=np.zeros(m);best_choices=np.zeros(len(D),dtype=int)
 observed=0;history=[];master=-np.inf;w=caps.copy()
 for iteration in range(max_iterations):
  val,ub,choices,margin=support(D,Du,w,budget)
  upper=min(float(m),float(np.nextafter(m+ub,np.inf)))
  observed=max(observed,int((margin>1e-8).sum()))
  if upper<best:best=upper;bestw=w.copy();best_choices=choices.copy()
  cuts.append(margin)
  A=np.column_stack((np.asarray(cuts),-np.ones(len(cuts))))
  result=linprog(np.r_[np.zeros(m),1.],A_ub=A,b_ub=np.zeros(len(cuts)),bounds=list(zip(np.zeros(m),caps))+[(None,None)],method='highs',options={'dual_feasibility_tolerance':1e-8,'primal_feasibility_tolerance':1e-8,'threads':1})
  if not result.success:
   history.append({'iteration':iteration,'upper':best,'solver_success':False,'status':int(result.status),'message':str(result.message)});break
  master=float(m+result.fun)
  history.append({'iteration':iteration,'upper':best,'master_lower':master,'gap':best-master,'solver_success':True})
  if best-master<=tolerance*max(1,abs(best)):break
  w=np.minimum(np.maximum(result.x[:-1],0),caps)
 assert best>=-1e-6
 return {'upper_count':max(0.,best),'weights':bestw.tolist(),'iterations':len(history),'master_lower':master,
  'envelope_gap':best-master,'history':history,'choices':best_choices.tolist(),'observed_strict_count':observed}

def retention(scores,features,ranking,bmax=3,max_iterations=40):
 """Upper bound worst-tie rank of the clean winner, over the whole corpus."""
 ref=int(ranking[0]);outside=np.asarray(ranking[1:]);lo,hi=outward_scores(scores,features)
 point,L,U=ranges(scores,lo,hi,ref,outside,bmax)
 answer=[]
 for b in range(1,bmax+1):
  keep=U[b]>=0;candidate=outside[keep]
  D=[f[:,candidate]-f[:,ref,None] for f in scores]
  Du=[np.nextafter(h[:,candidate]-l[:,ref,None],np.inf) for l,h in zip(lo,hi)]
  started=time.perf_counter();e=envelope(D,Du,L[b,keep],b,max_iterations);e['envelope_seconds']=time.perf_counter()-started
  e.update({'budget':b,'reference':ref,'candidate_indices':candidate.tolist(),'pairwise_upper_count':int(keep.sum()),
    'pairwise_rank_upper':int(keep.sum())+1,'rank_upper':int(np.floor(np.nextafter(e['upper_count'],np.inf)))+1,
    'strict_top1_certified':bool((U[b]<0).all()),'max_pair_margin':float(point[b].max(initial=-np.inf)),'max_pair_upper':float(U[b].max(initial=-np.inf))})
  answer.append(e)
 return answer

def direct_reference(D,Du,lower,budget):
 """Generic compact primal LP; validate its dual weights with the same oracle.
 An important matched comparator: no assumption the cutting-plane solver is faster.
 """
 m=len(lower)
 if not m:return {'upper_count':0.,'lp_objective':0.,'success':True,'variables':0,'constraints':0}
 lower=np.minimum(np.asarray(lower),-1e-8);caps=np.nextafter(1/(-lower),0.)
 S=sum(len(d) for d in D);allD=np.concatenate(D,axis=0)
 A=sparse.hstack((-sparse.csr_matrix(allD.T*caps[:,None]),sparse.eye(m)),format='csr')
 changed=np.concatenate([np.r_[0.,np.ones(len(d)-1)] for d in D])
 A=sparse.vstack((A,sparse.csr_matrix(np.r_[changed,np.zeros(m)][None,:])),format='csr')
 eq=sparse.lil_matrix((len(D),S+m));off=0
 for i,d in enumerate(D):eq[i,off:off+len(d)]=1;off+=len(d)
 r=linprog(np.r_[np.zeros(S),-np.ones(m)],A_ub=A,b_ub=np.r_[np.ones(m),budget],A_eq=eq.tocsr(),b_eq=np.ones(len(D)),bounds=[(0,1)]*(S+m),method='highs',options={'threads':1})
 out={'success':bool(r.success),'variables':S+m,'constraints':m+1+len(D),'status':int(r.status)}
 if r.success:
  w=np.minimum(np.maximum(-r.ineqlin.marginals[:m]*caps,0.),caps)
  _,u,choices,margin=support(D,Du,w,budget)
  out.update({'lp_objective':float(-r.fun),'upper_count':max(0.,min(float(m),float(np.nextafter(m+u,np.inf)))),'weights':w.tolist(),'choices':choices.tolist()})
 return out
