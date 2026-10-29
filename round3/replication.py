"""Independent second-stage replication on previously unevaluated query inputs.
Prepare and publish its freeze BEFORE running any new-query metrics.
"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[k]='1'
import argparse,hashlib,json,time
from pathlib import Path
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
from core import ROOT,Index,normalize,metrics
from replay import predict,apply,peak
from run import CONFIG,RES,CACHE,sources,qrels,native

def effective(text):return ' '.join(normalize(text).split()[:32])

def prepare():
 audit={};allids={}
 for ds in CONFIG['datasets']:
  _,q=sources(ds);texts=dict(zip(q['_id'],q['text']));rel=qrels(ds,'confirmation')
  dev=json.loads((RES/(ds+'_screen_ids.json')).read_text());primary=json.loads((RES/(ds+'_confirmation_ids.json')).read_text())
  seen_ids=set(dev+primary);seen_text={effective(texts[q]) for q in seen_ids};selected=[];excluded=[]
  for qid in sorted(rel,key=lambda q:hashlib.sha256((ds+'|replication|'+q).encode()).hexdigest()):
   if qid in seen_ids:continue
   key=effective(texts[qid])
   if key in seen_text:excluded.append({'query_id':qid,'reason':'effective_input_already_evaluated_or_duplicate'});continue
   selected.append(qid);seen_text.add(key)
  allids[ds]=selected;audit[ds]={'official_test_queries':len(rel),'primary_queries':len(primary),'fresh_queries':len(selected),'excluded':excluded,'development_queries':len(dev)}
 (RES/'replication_ids.json').write_text(json.dumps(allids,indent=2));(RES/'replication_selection_audit.json').write_text(json.dumps(audit,indent=2))
 # Primary evidence is locked before looking at new-query results, not pooled.
 names=['confirmation_summary.csv','paired_differences.csv','analysis_manifest.json']+[ds+'_retention_confirmation.jsonl' for ds in CONFIG['datasets']]
 lock={p:hashlib.sha256((RES/p).read_bytes()).hexdigest() for p in names}
 (RES/'primary_results_lock.json').write_text(json.dumps(lock,indent=2))
 print(json.dumps(audit,indent=2))

def freeze():
 if any(RES.glob('*_independent_replication.jsonl')):raise RuntimeError('New-query replication outputs already exist')
 f=json.loads((RES/'confirmation_freeze.json').read_text())
 extra=['replay.py','replication.py','PROTOCOL_REPLICATION.md','results/replication_ids.json','results/replication_selection_audit.json','results/primary_results_lock.json']
 files=dict(f['files']);files.update({p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in extra})
 out={'unix_time':time.time(),'method_preconfirmation_commit':'8dd7972dc13d85159e908f9b6ea03c394289acd2','new_metrics_exist':False,'primary_target':{'budget':2,'k':10,'baseline':'best_lp_enum','family_size':3,'alpha':.05},'files':files}
 (RES/'replication_freeze.json').write_text(json.dumps(out,indent=2));print('Independent replication frozen',len(files),'files')

def evaluate(ds):
 f=json.loads((RES/'replication_freeze.json').read_text())
 for p,h in f['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 ids=json.loads((RES/'replication_ids.json').read_text())[ds]
 _,q=sources(ds);texts=dict(zip(q['_id'],q['text']));rel=qrels(ds,'confirmation')
 I=Index.load(CACHE/(ds+'_char.pkl'));I.transpose();out=RES/(ds+'_independent_replication.jsonl')
 if out.exists():raise RuntimeError('Refuse to overwrite '+str(out))
 for i,qid in enumerate(ids):
  text=effective(texts[qid]);start=time.perf_counter();p,detail=predict(I,text,'proposed',budget_max=2,audit_details=True)
  direct,dd=predict(I,text,'direct_lp_enum',budget_max=2,audit_details=True);d=detail[1]
  if d.get('zero_reference'):pair=best=I.n
  else:pair=min(d['pair'],d['enum'] if d.get('enum') is not None else d['pair']);best=min(pair,d['lp'],direct[1])
  ranking=np.lexsort((I.ids,-I.score(text)));target=int(ranking[0]);judged=rel[qid].get(str(I.ids[target]),0)>0
  checks=[]
  lp=d.get('lp_certificate')
  if lp:
   q0=I.query(text);choices=lp['choices'];z=I.score(q0.text(choices));observed=1+int((z>z[target]+1e-8).sum())
   assert observed<=p[1];checks.append({'source':'support','observed_strict_rank':observed,'operations':q0.trace(choices)})
  row={'dataset':ds,'query_id':qid,'budget':2,'k':10,'corpus':I.n,'original_tokens':len(normalize(texts[qid]).split()),'used_tokens':len(text.split()),
   'reference_id':str(I.ids[target]),'reference_relevant':judged,'clean_metrics':metrics(ranking,I.ids,rel[qid]),
   'pair_enum_rank_upper':pair,'best_lp_enum_rank_upper':best,'proposed_rank_upper':p[1],'proposed_details':d,'direct_details':dd[1],
   'witness_checks':checks,'seconds':time.perf_counter()-start,'peak_process_mib':peak()}
  with out.open('a') as g:g.write(json.dumps(native(row))+'\n')
  print(ds,'independent replication',i+1,'/',len(ids),'pair',pair,'bestLP',best,'proposed',p[1],flush=True)
 (RES/(ds+'_replication_runtime.json')).write_text(json.dumps({'blas':[{'api':t['internal_api'],'threads':t['num_threads']} for t in threadpool_info()],'peak_process_mib':peak(),'queries':len(ids)},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','freeze','run']);p.add_argument('--dataset');a=p.parse_args()
 with threadpool_limits(limits=1):
  if a.command=='prepare':prepare()
  elif a.command=='freeze':freeze()
  else:evaluate(a.dataset)
