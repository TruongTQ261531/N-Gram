"""Discrete pair incompatibility and conservative clique-cover rank bounds.
Graph coloring, Pareto DP and support separation are established machinery.
"""
import numpy as np
from rank_bound import support

def pareto(points):
 if not len(points):return points
 order=np.lexsort((-points[:,1],-points[:,0]));p=points[order]
 keep=[];best=-np.inf
 for i,v in enumerate(p):
  if v[1]>best:keep.append(i);best=v[1]
 return p[keep]

def incompatible(D,Du,budget,max_points=20000,max_front=1000):
 """Prove no allowed query makes BOTH competitor margins nonnegative.
 Returning unknown/compatible never creates an incompatibility edge.
 """
 _,upper,_,_=support(D,Du,np.array([.5,.5]),budget)
 if upper<0:return {'incompatible':True,'method':'support','upper':upper,'peak_front':0}
 front=[np.array([[0.,0.]])]+[np.empty((0,2)) for _ in range(budget)]
 peak=1
 for u in Du:
  new=[]
  for b in range(budget+1):
   raw=np.nextafter(front[b]+u[0],np.inf)
   if b and len(front[b-1]) and len(u)>1:
    size=len(front[b-1])*(len(u)-1)+len(raw)
    if size>max_points:return {'incompatible':False,'method':'resource_cap','peak_front':peak}
    changed=np.nextafter(front[b-1][:,None,:]+u[None,1:,:],np.inf).reshape(-1,2)
    both=np.vstack((raw,changed))
   else:both=raw
   f=pareto(both);peak=max(peak,len(f))
   if len(f)>max_front:return {'incompatible':False,'method':'resource_cap','peak_front':peak}
   new.append(f)
  front=new
 value=max((np.minimum(f[:,0],f[:,1]).max(initial=-np.inf) for f in front),default=-np.inf)
 return {'incompatible':bool(value<0),'method':'pareto','upper':float(value),'peak_front':peak}

def cover_bound(D,Du,budget,max_checks=120,max_candidates=80):
 m=D[0].shape[1] if D else 0
 if m>max_candidates:return {'count_upper':m,'groups':[[j] for j in range(m)],'checks':[],'skipped':'candidate_resource_cap'}
 groups=[];checks=[];cache={}
 for j in range(m):
  placed=False
  for group in groups:
   okay=True
   for k in group:
    pair=(min(j,k),max(j,k))
    if pair not in cache:
     if len(checks)>=max_checks:okay=False;break
     d=[a[:,pair] for a in D];u=[a[:,pair] for a in Du]
     result=incompatible(d,u,budget);result.update({'left':pair[0],'right':pair[1]});checks.append(result);cache[pair]=result['incompatible']
    if not cache[pair]:okay=False;break
   if okay:group.append(j);placed=True;break
  if not placed:groups.append([j])
 return {'count_upper':len(groups),'groups':groups,'checks':checks}
