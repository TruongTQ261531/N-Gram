"""Analyze all frozen confirmation queries. No tuning or row filtering."""
from pathlib import Path
import gzip,json,math
import numpy as np
import pandas as pd
from scipy.stats import binomtest
ROOT=Path(__file__).resolve().parent;R=ROOT/'results'
DATASETS=['scifact','nfcorpus','fiqa'];KS=[1,5,10,20,50]

def load(ds):
 p=R/(ds+'_retention_confirmation.jsonl')
 if p.exists():return [json.loads(x) for x in p.read_text().splitlines()]
 with gzip.open(str(p)+'.gz','rt') as f:return [json.loads(x) for x in f]

def ranks(e):
 pair=int(e['pairwise_rank_upper']);en=e['enumeration'].get('rank_upper',pair)
 lp=int(e['lp_rank_upper']);direct=e['direct_lp']
 if direct.get('success') and 'rank_upper' in direct:lp=min(lp,int(direct['rank_upper']))
 m=e['mip_reference'];mip=pair
 if m.get('count_upper') is not None:mip=int(math.floor(np.nextafter(m['count_upper']+1e-6,np.inf)))+1
 return {'coarse':int(e['coarse_rank_upper']),'pairwise':pair,'pair_enum':min(pair,en),
  'best_lp_enum':min(pair,en,lp),'proposed':int(e['rank_upper']),'mip_enum':min(pair,en,mip)}

def main():
 summary=[];paired=[];rows=[];quality=[];solver=[];schema={}
 for di,ds in enumerate(DATASETS):
  a=load(ds);expected=json.loads((R/(ds+'_confirmation_ids.json')).read_text())
  assert len(a)==100 and [x['query_id'] for x in a]==expected
  idx=np.random.default_rng(20261029+di).integers(0,len(a),(2000,len(a)))
  np.savez_compressed(R/(ds+'_bootstrap_indices.npz'),indices=idx)
  judged=np.array([x['reference_relevant'] for x in a],bool)
  quality.append({'dataset':ds,'queries':len(a),'judged_relevant_winner':judged.mean(),'truncated':sum(x['truncated'] for x in a),
   'char_ndcg10':np.mean([x['char_metrics']['ndcg10'] for x in a]),'word_ndcg10':np.mean([x['word_metrics']['ndcg10'] for x in a]),
   'char_recall10':np.mean([x['char_metrics']['recall10'] for x in a]),'word_recall10':np.mean([x['word_metrics']['recall10'] for x in a])})
  for b in [1,2,3]:
   e=[x['bounds'][b-1] for x in a];bound={k:np.array([ranks(z)[k] for z in e]) for k in ranks(e[0])}
   for qi,(x,z) in enumerate(zip(a,e)):
    observed=max([z['support_observed_strict_rank']]+[d['max_observed_strict_rank'] for d in x['diagnostics'] if d['budget']==b])
    assert observed<=z['rank_upper']
    m=z['mip_reference'];invalid=m.get('count_upper') is not None and observed>math.floor(m['count_upper']+1e-6)+1
    if invalid:raise RuntimeError('Numerical MIP upper contradicted by observed rank: '+ds+'/'+x['query_id'])
    rows.append({'dataset':ds,'query_id':x['query_id'],'budget':b,'reference_relevant':x['reference_relevant'],
     'observed_strict_rank':observed,**{k:int(v[qi]) for k,v in bound.items()}})
    solver.append({'dataset':ds,'query_id':x['query_id'],'budget':b,'candidates':z['pairwise_upper_count'],
     'lp_iterations':z['iterations'],'lp_gap':z.get('envelope_gap'),'graph_checks':len(z['graph'].get('checks',[])),
     'graph_edges':sum(t.get('incompatible',False) for t in z['graph'].get('checks',[])),
     'pareto_unknown':sum(t.get('method')=='resource_cap' for t in z['graph'].get('checks',[])),
     'graph_skipped':z['graph'].get('skipped'),'enum_skipped':z['enumeration'].get('skipped'),
     'mip_status':m.get('status'),'mip_success':m.get('success'),'mip_skipped':m.get('skipped'),
     'mip_total_seconds':m.get('total_seconds'),'direct_lp_success':z['direct_lp'].get('success')})
   for k in KS:
    cert={m:v<=k for m,v in bound.items()}
    for m,c in cert.items():
     boot=c[idx].mean(1);ci=np.quantile(boot,[.025,.975]);use=c&judged
     summary.append({'dataset':ds,'budget':b,'k':k,'method':m,'queries':len(a),'certified':int(c.sum()),'coverage':c.mean(),
      'ci_low':ci[0],'ci_high':ci[1],'judged_relevant_certified':int(use.sum()),'useful_coverage':use.mean()})
    for base in ['pair_enum','best_lp_enum','mip_enum']:
     d=cert['proposed'].astype(int)-cert[base].astype(int);boot=d[idx].mean(1);ci=np.quantile(boot,[.025,.975]);wins=int((d>0).sum());losses=int((d<0).sum())
     p=binomtest(wins,wins+losses,.5).pvalue if wins+losses else 1.
     paired.append({'dataset':ds,'budget':b,'k':k,'baseline':base,'difference':d.mean(),'ci_low':ci[0],'ci_high':ci[1],
      'wins':wins,'losses':losses,'paired_exact_p':p})
  schema[ds]={'queries':len(a),'random_diagnostic_samples':len(a)*3*3*10,'no_sampled_or_support_rank_violation':True}
 S=pd.DataFrame(summary);P=pd.DataFrame(paired)
 primary=P[(P.k==10)&P.baseline.isin(['pair_enum','best_lp_enum'])].sort_values('paired_exact_p')
 adjusted=np.maximum.accumulate(np.minimum(1,primary.paired_exact_p.to_numpy()*np.arange(len(primary),0,-1)))
 P.loc[primary.index,'holm_primary_p']=adjusted
 S.to_csv(R/'confirmation_summary.csv',index=False);P.to_csv(R/'paired_differences.csv',index=False)
 pd.DataFrame(rows).to_csv(R/'query_rank_bounds.csv',index=False);pd.DataFrame(quality).to_csv(R/'retrieval_quality.csv',index=False);pd.DataFrame(solver).to_csv(R/'solver_status.csv',index=False)
 (R/'analysis_manifest.json').write_text(json.dumps({'bootstrap_replicates':2000,'seed_base':20261029,'primary_k':10,'holm_family_size':len(primary),
  'query_counts':schema,'conditional_intervals':True,'q1_readiness':'not established by statistics alone'},indent=2))
 print(S[(S.k==10)&S.method.isin(['pair_enum','best_lp_enum','proposed'])][['dataset','budget','method','certified','queries']].to_string(index=False))
 print(P[(P.k==10)&P.baseline.isin(['pair_enum','best_lp_enum'])].to_string(index=False))
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,axes=plt.subplots(3,3,figsize=(11,9),sharey=True)
 for i,ds in enumerate(DATASETS):
  for j,b in enumerate([1,2,3]):
   ax=axes[i,j];methods=['pair_enum','best_lp_enum','proposed'];z=S[(S.dataset==ds)&(S.budget==b)&(S.k==10)].set_index('method').loc[methods]
   y=z.coverage.to_numpy()*100;err=np.vstack((y-z.ci_low.to_numpy()*100,z.ci_high.to_numpy()*100-y))
   ax.bar(range(3),y,color=['#9aa7b5','#5b8db8','#2c8b70'],yerr=np.maximum(err,0),capsize=3);ax.set_ylim(0,100)
   ax.set_xticks(range(3),['Pair+enum','LP+enum','Discrete'],rotation=15);ax.set_title(ds+' | token budget '+str(b))
   if j==0:ax.set_ylabel('Certified retention in top-10 (%)')
 fig.suptitle('Frozen confirmation: 100 queries per corpus, fixed character-BM25')
 fig.tight_layout();fig.savefig(R/'retention_coverage.png',dpi=170);fig.savefig(R/'retention_coverage.pdf');plt.close(fig)

if __name__=='__main__':main()
