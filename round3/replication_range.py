"""Execution-only ranged adapter of the frozen replication driver."""
import inspect
from replication import *

def verify_identity():
 original=inspect.getsource(evaluate)
 ranged=inspect.getsource(evaluate_range)
 ranged=ranged.replace('def evaluate_range(ds,start,end):','def evaluate(ds):').replace("[ds][start:end]","[ds]").replace("ds+'_replication_range_'+str(start)+'_'+str(end)+'.jsonl'","ds+'_independent_replication.jsonl'").replace("ds+'_replication_range_'+str(start)+'_'+str(end)+'_runtime.json'","ds+'_replication_runtime.json'")
 assert original.strip()==ranged.strip(),'Range adapter changed per-query computation'

def evaluate_range(ds,start,end):
 f=json.loads((RES/'replication_freeze.json').read_text())
 for p,h in f['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 ids=json.loads((RES/'replication_ids.json').read_text())[ds][start:end]
 _,q=sources(ds);texts=dict(zip(q['_id'],q['text']));rel=qrels(ds,'confirmation')
 I=Index.load(CACHE/(ds+'_char.pkl'));I.transpose();out=RES/(ds+'_replication_range_'+str(start)+'_'+str(end)+'.jsonl')
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
 (RES/(ds+'_replication_range_'+str(start)+'_'+str(end)+'_runtime.json')).write_text(json.dumps({'blas':[{'api':t['internal_api'],'threads':t['num_threads']} for t in threadpool_info()],'peak_process_mib':peak(),'queries':len(ids)},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dataset',required=True);p.add_argument('--start',type=int,required=True);p.add_argument('--end',type=int,required=True);a=p.parse_args()
 verify_identity()
 with threadpool_limits(limits=1):evaluate_range(a.dataset,a.start,a.end)
