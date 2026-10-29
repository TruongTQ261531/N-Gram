"""Postconfirmation diagnostic analyses; not a new held-out hypothesis test."""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import json,math,itertools
import numpy as np,pandas as pd
from analyze import load,ranks,R
from rank_bound import envelope,direct_reference
from compatibility import cover_bound
from mip_reference import solve
def partition(m,edges):
 groups=[]
 for j in range(m):
  for g in groups:
   if all((min(j,k),max(j,k)) in edges for k in g):g.append(j);break
  else:groups.append([j])
 return len(groups)+1
def main():
 rows=[];timing=[]
 for ds in ['scifact','nfcorpus','fiqa']:
  a=load(ds)
  for x in a:
   for z in x['bounds']:
    v=ranks(z);g=z['graph'];m=z['pairwise_upper_count']
    edges={(min(e['left'],e['right']),max(e['left'],e['right'])) for e in g.get('checks',[]) if e.get('incompatible') and e['method']=='support'}
    # Reuse exactly the recorded pair tests; this is NOT an independently
    # rerun support-only scheduler. Missing edges remain conservative.
    s=partition(m,edges) if m<=80 else m+1
    rows.append({'dataset':ds,'query_id':x['query_id'],'budget':z['budget'],'best_lp_enum':v['best_lp_enum'],
     'recorded_support_edges_cover':min(s,v['best_lp_enum']),'proposed':v['proposed'],
     'support_edges':len(edges),'pareto_edges':sum(e.get('incompatible',False) and e['method']=='pareto' for e in g.get('checks',[]))})
  replay=[json.loads(s) for s in (R/(ds+'_controlled_replay.jsonl')).read_text().splitlines()]
  for method in ['pair_enum','lp_enum','direct_lp_enum','proposed','mip_enum']:
   t=[p['seconds'] for x in replay for p in x['profile'] if p['method']==method]
   timing.append({'dataset':ds,'method':method,'profile_queries':len(t),'median_seconds':np.median(t),'p90_seconds':np.quantile(t,.9)})
 pd.DataFrame(rows).to_csv(R/'posthoc_edge_diagnostics.csv',index=False);pd.DataFrame(timing).to_csv(R/'controlled_latency.csv',index=False)
 toy=[]
 for M in [3,4,8]:
  D=[np.vstack((-np.ones((1,M)),np.eye(M)*(1+1/(M-1))-np.ones((M,M))/(M-1)))];Du=[np.nextafter(d,np.inf) for d in D];L=-np.ones(M)
  e=envelope(D,Du,L,1,40);direct=direct_reference(D,Du,L,1);g=cover_bound(D,Du,1,M*M,80);m=solve(Du,L,1,2.)
  exact=max(int((row>=0).sum()) for row in D[0]);assert exact==1 and g['count_upper']==1
  assert e['upper_count']>=M-1e-8 and direct['lp_objective']>=M-1e-8
  toy.append({'alternatives':M,'exact_count':exact,'lp_upper':e['upper_count'],'generic_lp_objective':direct['lp_objective'],'discrete_cover_upper':g['count_upper'],'mip':m,'graph':g})
 (R/'synthetic_gap_diagnostics.json').write_text(json.dumps({'scope':'generic additive factors, NOT an asserted physical BM25 keyboard realization','rows':toy},indent=2))
 print('Wrote recorded-edge ablation, isolated latency summary and 3 matched synthetic LP/discrete-gap cases')
if __name__=='__main__':main()
