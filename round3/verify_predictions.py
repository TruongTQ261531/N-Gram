"""Independently recompute metrics and paired tests from saved individual rows.
No corpus download, pickle, model execution or fitting is needed.
"""
from pathlib import Path
import gzip,json,math
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parent;R=ROOT/'results'
def load(name):
 p=R/name
 if p.exists():return [json.loads(x) for x in p.read_text().splitlines()]
 with gzip.open(str(p)+'.gz','rt') as f:return [json.loads(x) for x in f]
def exact(w,l):
 n=w+l
 return min(1.,2*sum(math.comb(n,i) for i in range(min(w,l)+1))/2**n) if n else 1.
def holm(values):
 order=np.argsort(values,kind='stable');out=np.zeros(len(values));last=0.
 for j,i in enumerate(order):last=max(last,min(1.,values[i]*(len(values)-j)));out[i]=last
 return out
def main():
 total=0
 for ds in ['scifact','nfcorpus','fiqa']:
  a=load(ds+'_retention_confirmation.jsonl');z=np.load(R/(ds+'_individual_predictions.npz'),allow_pickle=False)
  assert list(z['query_ids'])==[x['query_id'] for x in a]
  c=z['choices'];assert np.all(c>=0) and np.all(c<z['state_sizes'][:,None,None,None,:])
  assert np.all((c!=0).sum(-1)<=np.arange(1,4)[None,None,:,None])
  assert np.all(z['top_indices']>=0) and np.all(z['top_indices']<len(z['document_ids']))
  assert np.all(z['grades']>=0)
  denominator=z['ideal_dcg'];discount=np.log2(np.arange(2,12))
  ndcg=np.divide(((2**z['grades']-1)/discount).sum(-1),denominator[:,None,None,None],out=np.zeros_like(z['ranks'],dtype=float),where=denominator[:,None,None,None]>0)
  for qi,row in enumerate(a):
   assert list(z['document_ids'][z['clean_top'][qi]])==row['clean_top10']
   for prefix,old in [('clean','char_metrics'),('word','word_metrics')]:
    g=z[prefix+'_grades'][qi];d=float(((2**g-1)/discount).sum()/denominator[qi]) if denominator[qi] else 0.
    recall=float((g>0).sum()/z['positive_count'][qi]) if z['positive_count'][qi] else 0.
    assert abs(d-row[old]['ndcg10'])<1e-12 and abs(recall-row[old]['recall10'])<1e-12
   for si,seed in enumerate(z['seeds']):
    for bi,b in enumerate([1,2,3]):
     old=next(x for x in row['diagnostics'] if x['seed']==seed and x['budget']==b)
     assert abs(ndcg[qi,si,bi].mean()-old['sampled_ndcg10_mean'])<1e-12
     assert z['ranks'][qi,si,bi].max()==old['max_observed_strict_rank']
     assert np.all(z['ranks'][qi,si,bi]<=row['bounds'][bi]['rank_upper'])
   total+=90
  replay=load(ds+'_controlled_replay.jsonl');assert len(replay)==len(a)
  assert all(x['agreement'] and x['budget2_restriction_agreement'] for x in replay)
  runtime=json.loads((R/(ds+'_controlled_runtime.json')).read_text());assert all(x['threads']==1 for x in runtime['blas'])
 p=pd.read_csv(R/'paired_differences.csv')
 for row in p.itertuples():assert abs(exact(row.wins,row.losses)-row.paired_exact_p)<1e-12
 mask=(p.k==10)&p.baseline.isin(['pair_enum','best_lp_enum'])
 assert np.allclose(holm(p.loc[mask,'paired_exact_p'].to_numpy()),p.loc[mask,'holm_primary_p'],atol=1e-12)
 print('Verified',total,'individual sampled predictions, clean metrics, 300 full-corpus replay agreements, 300 B2 adapter agreements and independent exact/Holm tests')
if __name__=='__main__':main()
