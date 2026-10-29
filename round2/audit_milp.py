"""Independent MILP cross-check of exact DP on long, real inputs."""
import json,time
import numpy as np
from scipy import sparse
from scipy.optimize import milp,Bounds,LinearConstraint
from core import RES
from run import DS,load
from artifact import load_model
from lattice import exact_path
rows=[]
for ds in DS:
 en,W,labels=load_model(RES/(ds+'_bolt_model.npz'));_,_,te,_,_=load(ds)
 for r in te.head(5).itertuples():
  d=en.encode(r.text,r.row_id);n,q=d.ids.shape;u,e=en.potentials(W,d,en.tables(W));yy=int(np.asarray(en.features([d])@W).argmax(1)[0])
  for cc in range(len(labels)):
   if cc==yy:continue
   um=u[:,:,cc]-u[:,:,yy];em=e[:,:,:,cc]-e[:,:,:,yy];N=n*q+(n-1)*q*q
   def node(i,s):return i*q+s
   def edge(i,t,s):return n*q+(i-1)*q*q+t*q+s
   coef=np.r_[-um.ravel(),-em[1:].ravel()];rr=[];cols=[];vals=[];lo=[];hi=[];row=0
   def add(indices,values,low,high):
    global row
    rr.extend([row]*len(indices));cols.extend(indices);vals.extend(values);lo.append(low);hi.append(high);row+=1
   for i in range(n):add([node(i,s) for s in range(q)],[1.]*q,1.,1.)
   for i in range(1,n):
    for t in range(q):add([edge(i,t,s) for s in range(q)]+[node(i-1,t)],[1.]*q+[-1.],0.,0.)
    for s in range(q):add([edge(i,t,s) for t in range(q)]+[node(i,s)],[1.]*q+[-1.],0.,0.)
   add(list(range(n*q)),d.costs.ravel().astype(float).tolist(),-np.inf,3.)
   A=sparse.csc_matrix((vals,(rr,cols)),shape=(row,N))
   upper=np.ones(N)
   for i in range(n):
    for s in range(q):
     if d.costs[i,s]>3:upper[node(i,s)]=0
   t=time.perf_counter();fit=milp(coef,integrality=np.ones(N),bounds=Bounds(np.zeros(N),upper),constraints=LinearConstraint(A,np.array(lo),np.array(hi)),options={'time_limit':30,'mip_rel_gap':1e-9})
   assert fit.success and fit.status==0,(ds,r.row_id,fit.message)
   val,path=exact_path(np.ascontiguousarray(um),np.ascontiguousarray(em),d.costs,3);err=abs(val+fit.fun);assert err<1e-6
   witness=np.argmax(fit.x[:n*q].reshape(n,q),1);assert d.costs[np.arange(n),witness].sum()<=3
   rows.append({'dataset':ds,'row_id':int(r.row_id),'tokens':n,'competitor':cc,'dp_value':float(val),'milp_value':float(-fit.fun),'abs_difference':float(err),'milp_optimal':bool(fit.success),'mip_gap':float(fit.mip_gap),'seconds':time.perf_counter()-t})
(RES/'milp_audit.json').write_text(json.dumps(rows,indent=2));print('MILP cross-checks:',len(rows),'max error:',max(x['abs_difference'] for x in rows))
