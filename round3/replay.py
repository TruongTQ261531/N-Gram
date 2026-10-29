"""Controlled one-thread replay and individual sampled-prediction export.
Independent orchestration of frozen mathematical components, no method tuning.
"""
import os
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='1'
import argparse,gzip,hashlib,json,math,time
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
from core import ROOT,Index,normalize,metrics,outward_scores
from screening import coarse_candidates
from rank_bound import ranges,envelope,direct_reference
from compatibility import cover_bound
from enumeration import exhaustive_count
from mip_reference import solve as mip_solve
from run import CONFIG,CACHE,RES,sources,qrels,native

def peak():
 for line in Path('/proc/self/status').read_text().splitlines():
  if line.startswith('VmHWM:'):return int(line.split()[1])/1024

def predict(I,text,backend='proposed',fixture_prefix=None,budget_max=3,audit_details=False):
 query=I.query(text);ranking=query.rankings();c=coarse_candidates(query,ranking,budget_max);active=[b for b in range(1,budget_max+1) if not c['zero'][b]]
 if active:
  maximum=max(active);docs=np.array([c['ref']]+sorted(set(c['keep'][maximum])-{c['ref']}),dtype=int)
  W=I.W[docs].T.tocsr();F=[(A@W).toarray() for A in query.features];lo,hi=outward_scores(F,query.features)
  point,L,U=ranges(F,lo,hi,0,np.arange(1,len(docs)),maximum)
 result=[];details=[]
 for b in range(1,budget_max+1):
  if c['zero'][b]:result.append(I.n);details.append({'zero_reference':True,'reference_id':str(I.ids[c['ref']]),'choices':c['zero_choices']});continue
  keep=U[b]>=0;candidate=np.arange(1,len(docs))[keep];m=len(candidate)
  D=[f[:,candidate]-f[:,0,None] for f in F];Du=[np.nextafter(h[:,candidate]-l[:,0,None],np.inf) for l,h in zip(lo,hi)];lower=L[b,keep]
  enum=exhaustive_count(D,Du,b);rank=min(m+1,int(enum.get('rank_upper',m+1)));info={'pair':m+1,'enum':enum.get('rank_upper')}
  if audit_details:info.update({'candidate_ids':I.ids[docs[candidate]].tolist(),'reference_id':str(I.ids[c['ref']]),'enumeration_certificate':enum})
  if backend in ['proposed','lp_enum']:
   e=envelope(D,Du,lower,b,40);lr=int(np.floor(np.nextafter(e['upper_count'],np.inf)))+1;rank=min(rank,lr);info['lp']=lr
   if audit_details:info['lp_certificate']=e
  if backend=='proposed':
   g=cover_bound(D,Du,b,120,80);rank=min(rank,g['count_upper']+1);info['graph']=g['count_upper']+1
   if audit_details:info['graph_certificate']=g
  if backend=='direct_lp_enum' and sum(len(d) for d in D)*m<=2_000_000:
   e=direct_reference(D,Du,lower,b)
   if e.get('success'):rank=min(rank,int(np.floor(np.nextafter(e['upper_count'],np.inf)))+1)
   info['direct_success']=e.get('success')
   if audit_details:info['direct_certificate']=e
  if backend=='mip_enum':
   e=mip_solve(Du,lower,b,1.)
   if e.get('count_upper') is not None:rank=min(rank,int(np.floor(np.nextafter(e['count_upper']+1e-6,np.inf)))+1)
   info['mip_status']=e.get('status');info['mip_skipped']=e.get('skipped')
  if fixture_prefix is not None and b<=2 and sum(len(d) for d in D)*m<=2_000_000:
   arrays={'budget':np.array(b),'lower':lower,'sizes':np.array([len(d) for d in D]),'margins':np.concatenate(D,axis=0),'upper_margins':np.concatenate(Du,axis=0),
    'candidate_ids':I.ids[docs[candidate]],'reference_id':np.array(str(I.ids[c['ref']]))}
   np.savez_compressed(str(fixture_prefix)+'_b'+str(b)+'.npz',**arrays)
  result.append(rank);details.append(info)
 return result,details

def apply(tokens,operations):
 t=list(tokens);seen=set()
 for op in operations:
  i=op['token'];assert i not in seen;seen.add(i);s=t[i];p=op['pos']
  if op['op']=='delete':s=s[:p]+s[p+1:]
  elif op['op']=='repeat':s=s[:p]+s[p]+s[p:]
  elif op['op']=='keyboard':s=s[:p]+op['char']+s[p+1:]
  elif op['op']=='swap':s=s[:p]+s[p+1]+s[p]+s[p+2:]
  else:raise RuntimeError(op)
  t[i]=s
 return ' '.join(t)

def main(ds,profile_count):
 p=RES/(ds+'_retention_confirmation.jsonl')
 if p.exists():records=[json.loads(x) for x in p.read_text().splitlines()]
 else:
  with gzip.open(str(p)+'.gz','rt') as f:records=[json.loads(x) for x in f]
 assert len(records)==100
 _,queries=sources(ds);qtext=dict(zip(queries['_id'],queries['text']));rel=qrels(ds,'confirmation')
 start=time.perf_counter();I=Index.load(CACHE/(ds+'_char.pkl'));word=Index.load(CACHE/(ds+'_word.pkl'));I.transpose();word.transpose();startup=time.perf_counter()-start
 output=RES/(ds+'_controlled_replay.jsonl');output.write_text('');fixtures=RES/'fixtures';fixtures.mkdir(exist_ok=True)
 n=len(records);choices_all=np.zeros((n,3,3,10,32),np.int16);ranks=np.zeros((n,3,3,10),np.int32);grades=np.zeros((n,3,3,10,10));tops=np.zeros((n,3,3,10,10),np.int32)
 dcg=np.zeros(n);clean_top=np.zeros((n,10),np.int32);word_top=clean_top.copy();clean_grade=np.zeros((n,10));word_grade=clean_grade.copy();sizes=np.ones((n,32),np.int16);positive=np.zeros(n,np.int32)
 for qi,row in enumerate(records):
  qid=row['query_id'];text=' '.join(normalize(qtext[qid]).split()[:32]);expected=[b['rank_upper'] for b in row['bounds']]
  t=time.perf_counter();got,detail=predict(I,text,'proposed',fixtures/(ds+'_'+str(qi)) if qi<2 else None);elapsed=time.perf_counter()-t
  restricted,_=predict(I,text,'proposed',budget_max=2)
  profile=[]
  if qi<profile_count:
   methods=['pair_enum','lp_enum','direct_lp_enum','proposed','mip_enum'];shift=int(hashlib.sha256(qid.encode()).hexdigest(),16)%len(methods);methods=methods[shift:]+methods[:shift]
   for method in methods:
    t=time.perf_counter();rr,dd=predict(I,text,method);profile.append({'method':method,'seconds':time.perf_counter()-t,'rank_upper':rr,'details':dd})
  q=I.query(text);raw=I.score(text);ranking=q.rankings(raw);target=int(ranking[0]);clean_top[qi]=ranking[:10]
  wr=np.lexsort((word.ids,-word.score(text)));word_top[qi]=wr[:10]
  rdict=rel[qid];get_grades=lambda order:np.array([rdict.get(str(I.ids[j]),0.) for j in order],float)
  clean_grade[qi]=get_grades(ranking[:10]);word_grade[qi]=get_grades(wr[:10]);ideal=sorted(rdict.values(),reverse=True)[:10]
  dcg[qi]=sum((2**v-1)/math.log2(i+2) for i,v in enumerate(ideal));positive[qi]=sum(v>0 for v in rdict.values())
  sizes[qi,:len(q.tokens)]=[len(f) for f in q.forms]
  witness_checks=0
  for b in row['bounds']:
   for operations in [b['support_witness_operations'],b['mip_reference'].get('operations',[])]:
    assert len(operations)<=b['budget'];z=I.score(apply(q.tokens,operations));rank=1+int((z>z[target]+1e-8).sum());assert rank<=b['rank_upper'];witness_checks+=1
  for si,seed in enumerate(CONFIG['attack_seeds']):
   rng=np.random.default_rng(int(hashlib.sha256((qid+'|final|'+str(seed)).encode()).hexdigest()[:16],16))
   for bi,b in enumerate([1,2,3]):
    ndcg=[];observed=[]
    for sample in range(10):
     choices=np.zeros(len(q.tokens),int)
     for token in rng.choice(len(q.tokens),min(b,len(q.tokens)),replace=False):
      if len(q.forms[token])>1:choices[token]=rng.integers(1,len(q.forms[token]))
     z=I.score(q.text(choices));order=np.lexsort((I.ids,-z))[:10];rank=1+int((z>z[target]+1e-8).sum());assert rank<=row['bounds'][bi]['rank_upper']
     choices_all[qi,si,bi,sample,:len(choices)]=choices;ranks[qi,si,bi,sample]=rank;tops[qi,si,bi,sample]=order;grades[qi,si,bi,sample]=get_grades(order)
     ndcg.append(float(((2**grades[qi,si,bi,sample]-1)/np.log2(np.arange(2,12))).sum()/dcg[qi]) if dcg[qi] else 0.);observed.append(rank)
    old=next(d for d in row['diagnostics'] if d['seed']==seed and d['budget']==b)
    assert abs(np.mean(ndcg)-old['sampled_ndcg10_mean'])<1e-12
    assert max(observed)==old['max_observed_strict_rank']
  result={'dataset':ds,'query_id':qid,'expected_rank_upper':expected,'replayed_rank_upper':got,'agreement':got==expected,'budget2_restriction_agreement':restricted[1]==expected[1],'proposed_seconds':elapsed,'profile':profile,
   'reencoded_witnesses':witness_checks,'peak_process_mib':peak(),'details':detail}
  with output.open('a') as f:f.write(json.dumps(native(result))+'\n')
  print(ds,'controlled replay',qi+1,'/',n,'agreement',got==expected,'sec',round(elapsed,3),flush=True)
 np.savez_compressed(RES/(ds+'_individual_predictions.npz'),query_ids=np.array([x['query_id'] for x in records]),document_ids=I.ids,choices=choices_all,state_sizes=sizes,
  ranks=ranks,grades=grades,top_indices=tops,ideal_dcg=dcg,positive_count=positive,clean_top=clean_top,word_top=word_top,clean_grades=clean_grade,word_grades=word_grade,seeds=np.array(CONFIG['attack_seeds']))
 metadata={'dataset':ds,'startup_load_transpose_seconds':startup,'blas':[{'api':x['internal_api'],'threads':x['num_threads']} for x in threadpool_info()],
  'peak_process_mib':peak(),'profile_queries':profile_count,'replayed_queries':n,'warmed_index':True,'includes_jit':False}
 (RES/(ds+'_controlled_runtime.json')).write_text(json.dumps(metadata,indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dataset',required=True);p.add_argument('--profile-count',type=int,default=10);a=p.parse_args()
 with threadpool_limits(limits=1):main(a.dataset,a.profile_count)
