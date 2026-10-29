"""Offline structural/statistical verification. Does not replace corpus replay.
Uses original record rows, independent counts and the saved bootstrap indices.
"""
from pathlib import Path
import gzip,hashlib,json,math,subprocess,sys
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent;R=ROOT/'results'
subprocess.run([sys.executable,str(ROOT/'verify_freeze.py')],check=True)
S=pd.read_csv(R/'confirmation_summary.csv');P=pd.read_csv(R/'paired_differences.csv')
checked=0;edges=0;attacks=0
for ds in ['scifact','nfcorpus','fiqa']:
 p=R/(ds+'_retention_confirmation.jsonl')
 if p.exists():a=[json.loads(x) for x in p.read_text().splitlines()]
 else:
  with gzip.open(str(p)+'.gz','rt') as f:a=[json.loads(x) for x in f]
 expected=json.loads((R/(ds+'_confirmation_ids.json')).read_text());assert len(a)==100 and [x['query_id'] for x in a]==expected
 idx=np.load(R/(ds+'_bootstrap_indices.npz'),allow_pickle=False)['indices'];assert idx.shape==(2000,100)
 for b in [1,2,3]:
  vectors={m:[] for m in S.method.unique()}
  for x in a:
   z=x['bounds'][b-1];pair=int(z['pairwise_rank_upper']);en=int(z['enumeration'].get('rank_upper',pair));lp=int(z['lp_rank_upper'])
   direct=z['direct_lp']
   if direct.get('success') and 'rank_upper' in direct:lp=min(lp,int(direct['rank_upper']))
   mip=pair
   if z['mip_reference'].get('count_upper') is not None:mip=math.floor(np.nextafter(z['mip_reference']['count_upper']+1e-6,np.inf))+1
   values={'coarse':z['coarse_rank_upper'],'pairwise':pair,'pair_enum':min(pair,en),'best_lp_enum':min(pair,en,lp),'proposed':z['rank_upper'],'mip_enum':min(pair,en,mip)}
   assert z['rank_upper']==min(z['lp_rank_upper'],z['graph_rank_upper'],en)
   if not z['zero_reference_shortcut']:
    m=len(z['candidate_ids']);assert m==z['pairwise_upper_count']
    g=z['graph']
    if 'groups' in g:
     assert sorted(j for group in g['groups'] for j in group)==list(range(m))
     verified={(min(t['left'],t['right']),max(t['left'],t['right'])) for t in g['checks'] if t.get('incompatible')}
     for t in g['checks']:
      if t.get('incompatible'):assert t['upper']<0;edges+=1
     for group in g['groups']:
      for i,j in enumerate(group):
       for k in group[i+1:]:assert (min(j,k),max(j,k)) in verified
     assert len(g['groups'])+1==z['graph_rank_upper']
   observed=[z['support_observed_strict_rank']]+[d['max_observed_strict_rank'] for d in x['diagnostics'] if d['budget']==b]
   assert max(observed)<=z['rank_upper'];attacks+=len(observed)-1
   for m,v in values.items():vectors[m].append(int(v))
  for k in [1,5,10,20,50]:
   for method,v in vectors.items():
    cert=np.asarray(v)<=k;row=S[(S.dataset==ds)&(S.budget==b)&(S.k==k)&(S.method==method)].iloc[0]
    assert row.certified==int(cert.sum());assert abs(row.coverage-cert.mean())<1e-12
    ci=np.quantile(cert[idx].mean(1),[.025,.975]);assert abs(row.ci_low-ci[0])<1e-12 and abs(row.ci_high-ci[1])<1e-12;checked+=1
   for base in ['pair_enum','best_lp_enum','mip_enum']:
    d=(np.asarray(vectors['proposed'])<=k).astype(int)-(np.asarray(vectors[base])<=k).astype(int)
    row=P[(P.dataset==ds)&(P.budget==b)&(P.k==k)&(P.baseline==base)].iloc[0]
    assert row.wins==int((d>0).sum()) and row.losses==int((d<0).sum());assert abs(row.difference-d.mean())<1e-12
    ci=np.quantile(d[idx].mean(1),[.025,.975]);assert abs(row.ci_low-ci[0])<1e-12 and abs(row.ci_high-ci[1])<1e-12
if (ROOT/'checksums.sha256').exists():
 for line in (ROOT/'checksums.sha256').read_text().splitlines():
  h,n=line.split('  ',1);assert hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,n
print('Verified',checked,'summary rows;',edges,'stored incompatibility edges; 300 queries and all recorded observed-rank checks')
print('Structural/statistical verification only; full corpus re-encoding and numerical audits are separate.')
