"""Generic mixed-integer reference for the SAME discrete query/count problem.
This is a numerical solver audit/comparator, not a newly invented optimizer.
"""
import time
import numpy as np
from scipy import sparse
from scipy.optimize import milp,Bounds,LinearConstraint

def solve(Du,lower,budget,seconds=1.):
 m=len(lower);sizes=[len(d) for d in Du];S=sum(sizes)
 if not m:return {'success':True,'optimal_count':0,'count_upper':0.,'seconds':0.,'status':0,'choices':[0]*len(Du),'gap':0.}
 if S*m>2_000_000:return {'skipped':'matrix_entries_resource_cap','matrix_entries':S*m}
 L=np.minimum(np.asarray(lower),-1e-8);caps=1/(-L)
 matrix=np.concatenate(Du,axis=0)
 A=sparse.hstack((-sparse.csr_matrix(matrix.T*caps[:,None]),sparse.eye(m)),format='csr')
 budgetrow=np.concatenate([np.r_[0.,np.ones(n-1)] for n in sizes]+[np.zeros(m)])
 rows=[A,sparse.csr_matrix(budgetrow[None,:])];lo=[np.full(m,-np.inf),[-np.inf]];hi=[np.ones(m),[budget]]
 off=0;eq=sparse.lil_matrix((len(sizes),S+m))
 for i,n in enumerate(sizes):eq[i,off:off+n]=1;off+=n
 rows.append(eq.tocsr());lo.append(np.ones(len(sizes)));hi.append(np.ones(len(sizes)))
 c=np.r_[np.zeros(S),-np.ones(m)];start=time.perf_counter()
 r=milp(c,integrality=np.ones(S+m),bounds=Bounds(np.zeros(S+m),np.ones(S+m)),constraints=LinearConstraint(sparse.vstack(rows,format='csc'),np.concatenate(lo),np.concatenate(hi)),options={'time_limit':seconds,'mip_rel_gap':0.,'threads':1})
 result={'seconds':time.perf_counter()-start,'success':bool(r.success),'status':int(r.status),'message':str(r.message),'matrix_entries':S*m,'variables':S+m}
 if getattr(r,'mip_dual_bound',None) is not None:
  result['count_upper']=min(float(m),float(-r.mip_dual_bound));result['gap']=float(r.mip_gap);result['nodes']=int(r.mip_node_count)
 if r.x is not None:
  choices=[];off=0
  for n in sizes:choices.append(int(r.x[off:off+n].argmax()));off+=n
  result['choices']=choices;result['feasible_count']=float(-r.fun)
  if r.success:result['optimal_count']=int(round(-r.fun))
 return result
