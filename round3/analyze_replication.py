"""Analyze the independently preregistered second stage, never pool stages."""
import json,hashlib,math
import numpy as np,pandas as pd
from scipy.stats import binomtest
from pathlib import Path
from verify_predictions import load,holm
R=Path(__file__).resolve().parent/'results'
def main():
 ids=json.loads((R/'replication_ids.json').read_text());summary=[];paired=[];query=[];status=[]
 for di,(ds,expected) in enumerate(ids.items()):
  a=load(ds+'_independent_replication.jsonl');assert [x['query_id'] for x in a]==expected
  assert len(a)==len(set(expected))
  n=len(a);idx=np.random.default_rng(20261101+di).integers(0,n,(2000,n));np.savez_compressed(R/(ds+'_replication_bootstrap.npz'),indices=idx)
  relevant=np.array([x['reference_relevant'] for x in a],bool);v={m:np.array([x[m+'_rank_upper'] for x in a]) for m in ['pair_enum','best_lp_enum','proposed']}
  for m,bound in v.items():
   cert=bound<=10;ci=np.quantile(cert[idx].mean(1),[.025,.975])
   summary.append({'dataset':ds,'method':m,'queries':n,'certified':int(cert.sum()),'coverage':cert.mean(),'ci_low':ci[0],'ci_high':ci[1],
    'judged_relevant_winners':int(relevant.sum()),'judged_relevant_certified':int((cert&relevant).sum()),'useful_coverage':(cert&relevant).mean()})
  for base in ['pair_enum','best_lp_enum']:
   diff=(v['proposed']<=10).astype(int)-(v[base]<=10).astype(int);w=int((diff>0).sum());l=int((diff<0).sum());ci=np.quantile(diff[idx].mean(1),[.025,.975])
   paired.append({'dataset':ds,'baseline':base,'queries':n,'difference':diff.mean(),'ci_low':ci[0],'ci_high':ci[1],'wins':w,'losses':l,'paired_exact_p':binomtest(w,w+l,.5).pvalue if w+l else 1.})
  for x in a:
   d=x['proposed_details'];direct=x['direct_details'];lp=direct.get('direct_certificate',{})
   query.append({'dataset':ds,'query_id':x['query_id'],'reference_relevant':x['reference_relevant'],'clean_ndcg10':x['clean_metrics']['ndcg10'],
    **{m+'_rank_upper':x[m+'_rank_upper'] for m in v},'used_tokens':x['used_tokens'],'original_tokens':x['original_tokens']})
   status.append({'dataset':ds,'query_id':x['query_id'],'zero_reference':d.get('zero_reference',False),'candidates':len(d.get('candidate_ids',[])),
    'direct_success':lp.get('success'),'direct_status':lp.get('status'),'direct_cap_skip':not d.get('zero_reference',False) and 'direct_certificate' not in direct,
    'enum_skipped':d.get('enumeration_certificate',{}).get('skipped'),'graph_skipped':d.get('graph_certificate',{}).get('skipped'),
    'graph_checks':len(d.get('graph_certificate',{}).get('checks',[])),'graph_edges':sum(z.get('incompatible',False) for z in d.get('graph_certificate',{}).get('checks',[])),
    'lp_iterations':d.get('lp_certificate',{}).get('iterations'),'lp_gap':d.get('lp_certificate',{}).get('envelope_gap'),'concurrent_seconds':x['seconds']})
 P=pd.DataFrame(paired);mask=P.baseline=='best_lp_enum';P.loc[mask,'holm_primary_p']=holm(P.loc[mask,'paired_exact_p'].to_numpy())
 S=pd.DataFrame(summary);S.to_csv(R/'replication_summary.csv',index=False);P.to_csv(R/'replication_paired.csv',index=False)
 pd.DataFrame(query).to_csv(R/'replication_query_bounds.csv',index=False);pd.DataFrame(status).to_csv(R/'replication_solver_status.csv',index=False)
 (R/'replication_analysis_manifest.json').write_text(json.dumps({'independent_stage':True,'pooled_with_primary':False,'target':{'budget':2,'k':10,'baseline':'best_lp_enum'},
  'bootstrap_replicates':2000,'seed_base':20261101,'holm_family_size':3,'queries':{d:len(q) for d,q in ids.items()},
  'original_method_commit':'8dd7972dc13d85159e908f9b6ea03c394289acd2','replication_precommit':'5fcf816da7d686427f518845c71e682d95626cee'},indent=2))
 print(S.to_string(index=False));print(P.to_string(index=False))
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(1,3,figsize=(10,3.6),sharey=True)
 for ax,(ds,selected) in zip(axes,ids.items()):
  z=S[S.dataset==ds].set_index('method').loc[['pair_enum','best_lp_enum','proposed']];y=z.coverage.to_numpy()*100
  err=np.maximum(0,np.vstack((y-z.ci_low.to_numpy()*100,z.ci_high.to_numpy()*100-y)))
  ax.bar(range(3),y,color=['#9aa7b5','#5b8db8','#2c8b70'],yerr=err,capsize=3);ax.set_xticks(range(3),['Pair+enum','LP+enum','Discrete'],rotation=15);ax.set_title(ds+' (n='+str(len(selected))+')');ax.set_ylim(0,100)
 axes[0].set_ylabel('Certified top-10 retention (%)');fig.suptitle('Independent replication, fixed token budget B=2');fig.tight_layout();fig.savefig(R/'independent_replication.png',dpi=170);fig.savefig(R/'independent_replication.pdf');plt.close(fig)
if __name__=='__main__':main()
