from pathlib import Path
import argparse,hashlib,json,resource,time
import numpy as np
from core import ROOT,Index,normalize,metrics,outward_scores,independent
from rank_bound import retention,ranges,direct_reference
from run import CACHE,RES,CONFIG,sources,qrels,native

def evaluate(ds,phase,limit,label):
 if phase=='confirmation':
  f=json.loads((RES/'confirmation_freeze.json').read_text())
  for p,h in f['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 _,q=sources(ds);texts=dict(zip(q['_id'],q['text']));rel=qrels(ds,phase)
 ids=json.loads((RES/(ds+'_'+phase+'_ids.json')).read_text())[:limit]
 I=Index.load(CACHE/(ds+'_char.pkl'));word=Index.load(CACHE/(ds+'_word.pkl'))
 out=RES/(ds+'_rank_'+label+'.jsonl');out.write_text('')
 for qi,qid in enumerate(ids):
  start=time.perf_counter();orig=normalize(texts[qid]);text=' '.join(orig.split()[:CONFIG['max_query_tokens']])
  t=time.perf_counter();query=I.query(text);raw=query.raw();ranking=query.rankings(raw);F=query.all_scores();pre_seconds=time.perf_counter()-t
  assert len(F)>0
  assert np.max(np.abs(raw-sum(f[0] for f in F)))<1e-8
  t=time.perf_counter();bound=retention(F,query.features,ranking,3,40);bound_seconds=time.perf_counter()-t
  lo,hi=outward_scores(F,query.features);U,L=independent(F,lo,hi,3);reference=int(ranking[0]);outside=ranking[1:]
  row={'dataset':ds,'phase':phase,'query_id':qid,'corpus':I.n,'tokens':len(F),'original_tokens':len(orig.split()),
   'truncated':len(orig.split())>len(F),'states':sum(len(f) for f in F),'reference_id':str(I.ids[reference]),
   'reference_relevant':rel[qid].get(str(I.ids[reference]),0)>0,'clean_top10':I.ids[ranking[:10]].tolist(),
   'char_metrics':metrics(ranking,I.ids,rel[qid]),'word_metrics':metrics(np.lexsort((word.ids,-word.score(text))),word.ids,rel[qid]),
   'preprocessing_seconds':pre_seconds,'bound_seconds':bound_seconds,'bounds':[],'diagnostics':[]}
  for b,e in enumerate(bound,1):
   candidate=np.array(e['candidate_indices'],dtype=int)
   point,l,u=ranges(F,lo,hi,reference,candidate,3) if len(candidate) else (None,None,None)
   D=[f[:,candidate]-f[:,reference,None] for f in F]
   Du=[np.nextafter(h[:,candidate]-l0[:,reference,None],np.inf) for l0,h in zip(lo,hi)]
   independent_count=int((np.nextafter(U[b,outside]-L[b,reference],np.inf)>=0).sum())
   assert e['rank_upper']<=e['pairwise_rank_upper']<=independent_count+1
   e['independent_rank_upper']=independent_count+1
   e['candidate_ids']=I.ids[candidate].tolist();e.pop('candidate_indices')
   e['support_witness_operations']=query.trace(e['choices'])
   actual=I.score(query.text(e['choices']));actual_rank=1+int((actual>actual[reference]+1e-8).sum())
   e['support_witness_observed_strict_rank']=actual_rank
   assert actual_rank<=e['rank_upper']
   entries=sum(len(d) for d in D)*len(candidate)
   if entries<=2_000_000:
    t=time.perf_counter();ref=direct_reference(D,Du,l[b] if len(candidate) else [],b);ref['seconds']=time.perf_counter()-t
    ref['matrix_entries']=entries
    if ref['success']:
     assert ref['upper_count']+1e-5>=e['observed_strict_count']
     ref['rank_upper']=int(np.floor(np.nextafter(ref['upper_count'],np.inf)))+1
    e['direct_lp']=ref
   else:e['direct_lp']={'skipped':'matrix_entries_resource_cap','matrix_entries':entries}
   e.pop('choices');row['bounds'].append(e)
  for seed in CONFIG['attack_seeds']:
   rng=np.random.default_rng(int(hashlib.sha256((qid+'|rank|'+str(seed)).encode()).hexdigest()[:16],16))
   for b in range(1,4):
    observed=[];quality=[]
    for _ in range(CONFIG['attack_samples_per_seed_budget']):
     choices=np.zeros(len(F),dtype=int)
     for pos in rng.choice(len(F),min(b,len(F)),replace=False):
      if len(F[pos])>1:choices[pos]=rng.integers(1,len(F[pos]))
     z=sum(f[a] for f,a in zip(F,choices));r=1+int((z>z[reference]+1e-8).sum());observed.append(r)
     assert r<=bound[b-1]['rank_upper'],(ds,qid,b,r,bound[b-1]['rank_upper'])
     rr=np.lexsort((I.ids,-z));quality.append(metrics(rr,I.ids,rel[qid])['ndcg10'])
    row['diagnostics'].append({'seed':seed,'budget':b,'max_observed_strict_rank':max(observed),'sampled_ndcg10_mean':float(np.mean(quality))})
  row['seconds']=time.perf_counter()-start;row['peak_process_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
  with out.open('a') as f:f.write(json.dumps(native(row),ensure_ascii=False)+'\n')
  print(ds,label,qi+1,'/',len(ids),'seconds',round(row['seconds'],2),'pair',[e['pairwise_rank_upper'] for e in bound],'joint',[e['rank_upper'] for e in bound],flush=True)
  del F,query,lo,hi

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dataset',required=True);p.add_argument('--phase',default='screen',choices=['screen','confirmation']);p.add_argument('--limit',type=int,default=20);p.add_argument('--label',default='screen');a=p.parse_args()
 evaluate(a.dataset,a.phase,a.limit,a.label)
