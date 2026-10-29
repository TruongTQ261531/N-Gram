"""Final candidate driver. Uses index screening, shared-query count bound and
generic LP comparator. Confirmation requires a frozen source/configuration record.
"""
import argparse,hashlib,json,resource,time
import numpy as np
from core import ROOT,Index,normalize,metrics,outward_scores
from rank_bound import ranges,direct_reference,retention
from screening import screened_retention
from compatibility import cover_bound
from enumeration import exhaustive_count
from mip_reference import solve as mip_solve
from run import CACHE,RES,CONFIG,sources,qrels,native

def evaluate(ds,phase,limit,label,audit_full=False):
 if phase=='confirmation':
  freeze=json.loads((RES/'confirmation_freeze.json').read_text())
  for p,h in freeze['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 _,q=sources(ds);texts=dict(zip(q['_id'],q['text']));rel=qrels(ds,phase)
 ids=json.loads((RES/(ds+'_'+phase+'_ids.json')).read_text())[:limit]
 I=Index.load(CACHE/(ds+'_char.pkl'));word=Index.load(CACHE/(ds+'_word.pkl'))
 I.transpose();word.transpose() # startup cost is excluded from warmed query measurements
 output=RES/(ds+'_retention_'+label+'.jsonl');output.write_text('')
 for qi,qid in enumerate(ids):
  start=time.perf_counter();orig=normalize(texts[qid]);text=' '.join(orig.split()[:CONFIG['max_query_tokens']])
  t=time.perf_counter();query=I.query(text);raw=query.raw();ranking=query.rankings(raw);encoding=time.perf_counter()-t
  t=time.perf_counter();bounds,coarse,docs,F=screened_retention(query,ranking,3,40);proposed_seconds=encoding+time.perf_counter()-t
  target=int(ranking[0])
  row={'dataset':ds,'phase':phase,'query_id':qid,'corpus':I.n,'tokens':len(query.tokens),'original_tokens':len(orig.split()),
   'truncated':len(orig.split())>len(query.tokens),'states':sum(a.shape[0] for a in query.features),'reference_id':str(I.ids[target]),
   'reference_relevant':rel[qid].get(str(I.ids[target]),0)>0,'clean_top10':I.ids[ranking[:10]].tolist(),
   'char_metrics':metrics(ranking,I.ids,rel[qid]),'word_metrics':metrics(np.lexsort((word.ids,-word.score(text))),word.ids,rel[qid]),
   'encoding_seconds':encoding,'base_pipeline_seconds':proposed_seconds,'proposed_seconds':proposed_seconds,'materialized_documents':len(docs) if F is not None else 0,'bounds':[],'diagnostics':[]}
  for b,e in enumerate(bounds,1):
   e['lp_rank_upper']=e['rank_upper'];e['lp_upper_count']=e.pop('upper_count')
   candidate=np.array(e['candidate_indices'],dtype=int)
   e['coarse_rank_upper']=int(len(set(coarse['keep'][b])-{target}))+1
   if not e['zero_reference_shortcut']:
    setup_started=time.perf_counter()
    # Map global candidate IDs to materialized local columns.
    columns={int(doc):i for i,doc in enumerate(docs)};ix=np.array([columns[int(doc)] for doc in candidate],dtype=int)
    keepcols=np.r_[columns[target],ix];Fc=[f[:,keepcols] for f in F]
    lo,hi=outward_scores(Fc,query.features);m=len(ix);local=np.arange(1,m+1)
    _,lower,_=ranges(Fc,lo,hi,0,local,3)
    D=[f[:,1:]-f[:,0,None] for f in Fc];Du=[np.nextafter(h[:,1:]-l[:,0,None],np.inf) for l,h in zip(lo,hi)]
    e['post_setup_seconds']=time.perf_counter()-setup_started;row['proposed_seconds']+=e['post_setup_seconds']
    t=time.perf_counter();enum=exhaustive_count(D,Du,b);enum['seconds']=time.perf_counter()-t
    if 'rank_upper' in enum:
     enum.pop('choices',None);e['rank_upper']=min(e['rank_upper'],enum['rank_upper'])
    e['enumeration']=enum
    row['proposed_seconds']+=enum['seconds']
    t=time.perf_counter();graph=cover_bound(D,Du,b,120,80);graph['seconds']=time.perf_counter()-t
    e['graph']=graph;e['graph_rank_upper']=graph['count_upper']+1;e['rank_upper']=min(e['lp_rank_upper'],e['graph_rank_upper'])
    row['proposed_seconds']+=graph['seconds']
    if 'rank_upper' in enum:e['rank_upper']=min(e['rank_upper'],enum['rank_upper'])
    entries=sum(len(d) for d in D)*m
    if entries<=2_000_000:
     t=time.perf_counter();ref=direct_reference(D,Du,lower[b],b);ref['seconds']=time.perf_counter()-t;ref['matrix_entries']=entries
     if ref['success']:
      ref['rank_upper']=int(np.floor(np.nextafter(ref['upper_count'],np.inf)))+1
      # Both methods bound the same relaxation; finite cuts may be looser.
      assert e['lp_upper_count']+1e-5>=ref['lp_objective']
     e['direct_lp']=ref
    else:e['direct_lp']={'skipped':'matrix_entries_resource_cap','matrix_entries':entries}
    mip_started=time.perf_counter();mip=mip_solve(Du,lower[b],b,1.);mip['total_seconds']=time.perf_counter()-mip_started
    if 'choices' in mip:
     mz=I.score(query.text(mip['choices']));mr=1+int((mz>mz[target]+1e-8).sum())
     assert mr<=e['rank_upper'],(ds,qid,b,mr,e['rank_upper'])
     mip['observed_strict_rank']=mr;mip['operations']=query.trace(mip.pop('choices'))
    e['mip_reference']=mip
   else:
    e['direct_lp']={'skipped':'exact_zero_reference_shortcut'};e['graph']={'skipped':'exact_zero_reference_shortcut','seconds':0.};e['graph_rank_upper']=e['rank_upper']
    e['enumeration']={'skipped':'exact_zero_reference_shortcut'};e['mip_reference']={'skipped':'exact_zero_reference_shortcut'}
   choices=e.pop('choices');e['support_witness_operations']=query.trace(choices)
   z=I.score(query.text(choices));observed=1+int((z>z[target]+1e-8).sum());assert observed<=e['rank_upper']
   e['support_observed_strict_rank']=observed
   e['candidate_ids']=I.ids[candidate].tolist();e.pop('candidate_indices')
   assert e['rank_upper']<=e['pairwise_rank_upper']<=e['coarse_rank_upper'] or e['zero_reference_shortcut']
   row['bounds'].append(e)
  if audit_full:
   t=time.perf_counter();allF=query.all_scores();full=retention(allF,query.features,ranking,3,40)
   row['full_reference_seconds']=time.perf_counter()-t
   row['full_reference_rank_upper']=[e['rank_upper'] for e in full]
   row['full_reference_pairwise_rank_upper']=[e['pairwise_rank_upper'] for e in full]
   for a,b in zip(bounds,full):
    assert a['lp_rank_upper']==b['rank_upper'],(ds,qid,a['budget'],a['lp_rank_upper'],b['rank_upper'])
    assert a['pairwise_rank_upper']==b['pairwise_rank_upper']
  for seed in CONFIG['attack_seeds']:
   rng=np.random.default_rng(int(hashlib.sha256((qid+'|final|'+str(seed)).encode()).hexdigest()[:16],16))
   for b in range(1,4):
    ranks=[];quality=[]
    for _ in range(CONFIG['attack_samples_per_seed_budget']):
     choices=np.zeros(len(query.tokens),dtype=int)
     for pos in rng.choice(len(query.tokens),min(b,len(query.tokens)),replace=False):
      if len(query.forms[pos])>1:choices[pos]=rng.integers(1,len(query.forms[pos]))
     z=I.score(query.text(choices));r=1+int((z>z[target]+1e-8).sum());ranks.append(r)
     assert r<=bounds[b-1]['rank_upper']
     rr=np.lexsort((I.ids,-z));quality.append(metrics(rr,I.ids,rel[qid])['ndcg10'])
    row['diagnostics'].append({'seed':seed,'budget':b,'max_observed_strict_rank':max(ranks),'sampled_ndcg10_mean':float(np.mean(quality))})
  row['seconds']=time.perf_counter()-start;row['peak_process_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
  with output.open('a') as f:f.write(json.dumps(native(row),ensure_ascii=False)+'\n')
  print(ds,label,qi+1,'/',len(ids),'seconds',round(row['seconds'],2),'docs',row['materialized_documents'],'pair',[e['pairwise_rank_upper'] for e in bounds],'joint',[e['rank_upper'] for e in bounds],flush=True)
  del query,F

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dataset',required=True);p.add_argument('--phase',choices=['screen','confirmation'],default='screen');p.add_argument('--limit',type=int,default=20);p.add_argument('--label',default='screen');p.add_argument('--audit-full',action='store_true');a=p.parse_args()
 evaluate(a.dataset,a.phase,a.limit,a.label,a.audit_full)
