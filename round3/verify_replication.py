"""Offline second-stage checks from ALL preregistered per-query outputs."""
import gzip,hashlib,json,math
from pathlib import Path
import numpy as np,pandas as pd
from verify_predictions import load,exact,holm
R=Path(__file__).resolve().parent/'results';ROOT=R.parent
def main():
 f=json.loads((R/'replication_freeze.json').read_text())
 for p,h in f['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 for p,h in json.loads((R/'primary_results_lock.json').read_text()).items():
  if (R/p).exists():b=(R/p).read_bytes()
  else:
   with gzip.open(str(R/p)+'.gz','rb') as g:b=g.read()
  assert hashlib.sha256(b).hexdigest()==h,p
 S=pd.read_csv(R/'replication_summary.csv');P=pd.read_csv(R/'replication_paired.csv');allids=json.loads((R/'replication_ids.json').read_text());total=0;edges=0
 for ds,expected in allids.items():
  a=load(ds+'_independent_replication.jsonl');assert [x['query_id'] for x in a]==expected
  previous=set(json.loads((R/(ds+'_confirmation_ids.json')).read_text())+json.loads((R/(ds+'_screen_ids.json')).read_text()));assert not previous.intersection(expected)
  idx=np.load(R/(ds+'_replication_bootstrap.npz'),allow_pickle=False)['indices'];assert idx.shape==(2000,len(a))
  vectors={m:np.array([x[m+'_rank_upper'] for x in a]) for m in ['pair_enum','best_lp_enum','proposed']}
  relevant=np.array([x['reference_relevant'] for x in a],bool)
  for x in a:
   d=x['proposed_details'];dd=x['direct_details'];assert x['budget']==2 and x['k']==10
   if d.get('zero_reference'):assert all(x[m+'_rank_upper']==x['corpus'] for m in vectors)
   else:
    enum=d.get('enum') if d.get('enum') is not None else d['pair'];pair=min(d['pair'],enum);direct=pair
    ref=dd.get('direct_certificate',{})
    if ref.get('success'):direct=min(pair,math.floor(np.nextafter(ref['upper_count'],np.inf))+1)
    assert x['pair_enum_rank_upper']==pair
    assert x['best_lp_enum_rank_upper']==min(pair,d['lp'],direct)
    assert x['proposed_rank_upper']==min(pair,d['lp'],d['graph'])
    g=d['graph_certificate'];m=len(d['candidate_ids']);assert len(set(d['candidate_ids']))==m
    assert sorted(j for group in g['groups'] for j in group)==list(range(m))
    es={(min(e['left'],e['right']),max(e['left'],e['right'])) for e in g['checks'] if e.get('incompatible')}
    for e in g['checks']:
     if e.get('incompatible'):assert e['upper']<0;edges+=1
    for group in g['groups']:
     for i,j in enumerate(group):
      for k in group[i+1:]:assert (min(j,k),max(j,k)) in es
    assert len(g['groups'])+1==d['graph']
   assert all(z['observed_strict_rank']<=x['proposed_rank_upper'] and len(z['operations'])<=2 for z in x['witness_checks'])
   total+=1
  for m,v in vectors.items():
   c=v<=10;row=S[(S.dataset==ds)&(S.method==m)].iloc[0];ci=np.quantile(c[idx].mean(1),[.025,.975]);assert row.certified==c.sum() and row.queries==len(a)
   assert abs(row.coverage-c.mean())<1e-12 and np.allclose(ci,[row.ci_low,row.ci_high],atol=1e-12)
   assert row.judged_relevant_certified==(c&relevant).sum()
  for baseline in ['pair_enum','best_lp_enum']:
   diff=(vectors['proposed']<=10).astype(int)-(vectors[baseline]<=10).astype(int);w=int((diff>0).sum());l=int((diff<0).sum());row=P[(P.dataset==ds)&(P.baseline==baseline)].iloc[0]
   assert row.wins==w and row.losses==l and abs(row.difference-diff.mean())<1e-12 and abs(row.paired_exact_p-exact(w,l))<1e-12
   assert np.allclose(np.quantile(diff[idx].mean(1),[.025,.975]),[row.ci_low,row.ci_high],atol=1e-12)
 mask=P.baseline=='best_lp_enum';assert np.allclose(holm(P.loc[mask,'paired_exact_p'].to_numpy()),P.loc[mask,'holm_primary_p'],atol=1e-12)
 audit=json.loads((R/'replication_text_disjointness.json').read_text())
 for ds,v in audit.items():
  previous=set(v['previous_effective_sha256'].values());new=list(v['replication_effective_sha256'].values());assert len(new)==len(allids[ds]) and len(new)==len(set(new)) and not previous.intersection(new)
 part=json.loads((ROOT/'audit/replication_partition.json').read_text());whole=load('fiqa_independent_replication.jsonl');prefix=load('fiqa_replication_retained_prefix.jsonl')
 assert len(prefix)==part['prefix_queries'] and whole[:len(prefix)]==prefix
 p=R/'fiqa_replication_retained_prefix.jsonl'
 if p.exists():b=p.read_bytes()
 else:
  with gzip.open(str(p)+'.gz','rb') as g:b=g.read()
 assert hashlib.sha256(b).hexdigest()==part['prefix_sha256']
 for start,end in part['ranges']:
  assert load('fiqa_replication_range_'+str(start)+'_'+str(end)+'.jsonl')==whole[start:end]
  runtime=json.loads((R/('fiqa_range_'+str(start)+'_'+str(end)+'_runtime.json')).read_text());assert runtime['queries']==end-start and all(x['threads']==1 for x in runtime['blas'])
 mechanism=pd.read_csv(R/'mechanism_summary.csv')
 for ds in allids:
  a=load(ds+'_independent_replication.jsonl');w=[x for x in a if x['proposed_rank_upper']<=10<x['best_lp_enum_rank_upper']];z=mechanism[(mechanism.stage=='independent')&(mechanism.dataset==ds)].iloc[0]
  assert z.wins==len(w) and z.positive_qrel_wins==sum(x['reference_relevant'] for x in w)
  assert all(x['direct_details']['direct_certificate']['success'] and x['direct_details']['direct_certificate']['lp_objective']>10+1e-6 for x in w)
 print('Verified independent stage:',total,'preregistered queries;',edges,'recorded conflict edges; disjoint ID/input hashes; all metric/bootstrap/exact/Holm recomputations')
 print('This is artifact verification; it does not substitute for full corpus certificate replay or peer review.')
if __name__=='__main__':main()
