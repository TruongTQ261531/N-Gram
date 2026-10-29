from pathlib import Path
import argparse,hashlib,json,os,sys,time,resource
import numpy as np
import pandas as pd
from core import ROOT,Index,normalize,metrics,certify

CACHE=ROOT/'cache';CACHE.mkdir(exist_ok=True)
RES=ROOT/'results';RES.mkdir(exist_ok=True)
CONFIG={'datasets':['scifact','nfcorpus','fiqa'],'screen_queries':20,'confirmation_queries':100,
 'max_query_tokens':32,'ngram_lengths':[3,4,5],'bm25_k1':1.2,'bm25_b':.75,'budget_max':3,'top_k':[1,5,10],
 'attack_seeds':[17,29,43],'attack_samples_per_seed_budget':10,
 'scope':'at most B original whitespace tokens, each raw or one allowed delete/swap/repeat/QWERTY-neighbor operation',
 'selection':'SHA256(dataset|phase|query-id), first fixed count; no score-dependent filtering',
 'retention_k':[1,5,10,20,50],'primary_retention_k':10,'envelope_max_cuts':40,
 'graph_max_checks':120,'graph_max_candidates':80,'pareto_max_points':20000,'pareto_max_front':1000,
 'enumeration_max_states':2000,'reference_max_matrix_entries':2000000,'mip_seconds':1.,'highs_threads':1}

def dump(path,x):path.write_text(json.dumps(x,indent=2,ensure_ascii=False))

def sources(ds):
 r=ROOT/'data'/ds
 c=pd.read_parquet(r/'source/corpus/corpus-00000-of-00001.parquet').fillna('')
 q=pd.read_parquet(r/'source/queries/queries-00000-of-00001.parquet').fillna('')
 c['_id']=c['_id'].astype(str);q['_id']=q['_id'].astype(str)
 c=c.sort_values('_id').reset_index(drop=True)
 return c,q

def qrels(ds,phase):
 r=ROOT/'data'/ds/'qrels'
 p=r/('test.tsv' if phase=='confirmation' else ('dev.tsv' if (r/'dev.tsv').exists() else 'train.tsv'))
 a=pd.read_csv(p,sep='\t',dtype={'query-id':str,'corpus-id':str})
 out={}
 for q,d,v in a.itertuples(index=False,name=None):out.setdefault(q,{})[d]=max(out.get(q,{}).get(d,0),float(v))
 return out

def select_ids(ds,phase,rel):
 n=CONFIG['confirmation_queries' if phase=='confirmation' else 'screen_queries']
 return sorted(rel,key=lambda q:hashlib.sha256((ds+'|'+phase+'|'+q).encode()).hexdigest())[:n]

def prepare(ds):
 c,q=sources(ds);stats={'dataset':ds,'corpus':len(c),'queries':len(q),'duplicate_ids':int(c['_id'].duplicated().sum())}
 assert stats['duplicate_ids']==0
 stats['identical_corpus_texts']=int((c['title']+' '+c['text']).map(normalize).duplicated().sum())
 texts=(c['title']+' '+c['text']).map(normalize).tolist()
 for kind in ['char','word']:
  p=CACHE/(ds+'_'+kind+'.pkl');start=time.perf_counter()
  if not p.exists():
   I=Index(texts,c['_id'].tolist(),kind);I.save(p)
  else:I=Index.load(p)
  stats[kind]={'vocabulary':len(I.v.vocabulary_),'nnz':int(I.W.nnz),'index_bytes':p.stat().st_size,'seconds':time.perf_counter()-start}
  print('prepared',ds,kind,stats[kind],flush=True);del I
 for phase in ['screen','confirmation']:
  rel=qrels(ds,phase);ids=select_ids(ds,phase,rel)
  assert set(ids)<=set(q['_id'])
  dump(RES/(ds+'_'+phase+'_ids.json'),ids)
  stats[phase]={'eligible_queries':len(rel),'selected_queries':len(ids)}
 dump(RES/(ds+'_data_audit.json'),stats)

def native(x):
 if isinstance(x,np.ndarray):return [native(a) for a in x]
 if isinstance(x,np.generic):return native(x.item())
 if isinstance(x,float) and not np.isfinite(x):return None
 if isinstance(x,dict):return {k:native(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [native(a) for a in x]
 return x

def evaluate(ds,phase):
 if phase=='confirmation':
  freeze=json.loads((RES/'confirmation_freeze.json').read_text())
  for name,h in freeze['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
 c,q=sources(ds);qtext=dict(zip(q['_id'],q['text']));rel=qrels(ds,phase)
 ids=json.loads((RES/(ds+'_'+phase+'_ids.json')).read_text())
 I=Index.load(CACHE/(ds+'_char.pkl'));word=Index.load(CACHE/(ds+'_word.pkl'))
 output=RES/(ds+'_'+phase+'.jsonl');output.write_text('')
 for qi,qid in enumerate(ids):
  start=time.perf_counter();original=normalize(qtext[qid]);tokens=original.split();text=' '.join(tokens[:CONFIG['max_query_tokens']])
  query=I.query(text);raw=query.raw();rank=query.rankings(raw);N=len(query.tokens)
  if not N:raise RuntimeError('Empty query retained: '+qid)
  score_start=time.perf_counter();F=query.all_scores();score_time=time.perf_counter()-score_start
  equality=float(np.max(np.abs(sum(f[0] for f in F)-raw)))
  assert equality<1e-8
  row={'dataset':ds,'phase':phase,'query_id':qid,'original_tokens':len(tokens),'used_tokens':N,'truncated':len(tokens)>N,
   'states':sum(len(f) for f in F),'corpus':I.n,'score_seconds':score_time,'feature_additivity_error':equality,
   'char_metrics':metrics(rank,I.ids,rel[qid]),'word_metrics':metrics(np.lexsort((word.ids,-word.score(text))),word.ids,rel[qid]),
   'clean_top10':I.ids[rank[:10]].tolist(),'certificates':{},'diagnostics':[],'witness_checks':[]}
  for k in CONFIG['top_k']:
   methods=['full','pruned'] if int(hashlib.sha256((qid+str(k)).encode()).hexdigest(),16)%2 else ['pruned','full']
   got={}
   for method in methods:
    t=time.perf_counter();r=certify(F,query.features,rank,k,CONFIG['budget_max'],method=='pruned');elapsed=time.perf_counter()-t
    got[method]=r
    row['certificates'][str(k)+'_'+method]={key:native(r[key]) for key in ['cert','loose','upper','point','pairs','all_pairs']}
    row['certificates'][str(k)+'_'+method]['seconds']=elapsed
   np.testing.assert_array_equal(got['full']['cert'],got['pruned']['cert'])
   for b in range(1,CONFIG['budget_max']+1):
    w=got['full']['witness'][b]
    if got['full']['point'][b]>1e-8:
     choices=w['choices'];z=I.score(query.text(choices));rr=query.rankings(z)
     changed=set(rank[:k])!=set(rr[:k]);assert changed,(qid,k,b)
     actual=float(z[w['outside']]-z[w['inside']]);assert actual>0
     assert abs(actual-got['full']['point'][b])<1e-8
     row['witness_checks'].append({'k':k,'budget':b,'operations':query.trace(choices),
       'inside_id':str(I.ids[w['inside']]),'outside_id':str(I.ids[w['outside']]),'margin':actual,
       'changed_top_k':changed,'perturbed_top10':I.ids[rr[:10]].tolist()})
  for seed in CONFIG['attack_seeds']:
   rng=np.random.default_rng(int(hashlib.sha256((qid+'|'+str(seed)).encode()).hexdigest()[:16],16))
   for b in range(1,CONFIG['budget_max']+1):
    values=[];stable={k:[] for k in CONFIG['top_k']}
    for _ in range(CONFIG['attack_samples_per_seed_budget']):
     choices=np.zeros(N,dtype=int)
     for t in rng.choice(N,min(b,N),replace=False):
      if len(F[t])>1:choices[t]=rng.integers(1,len(F[t]))
     z=sum(f[a] for f,a in zip(F,choices));rr=query.rankings(z)
     values.append(metrics(rr,I.ids,rel[qid])['ndcg10'])
     for k in CONFIG['top_k']:
      same=set(rank[:k])==set(rr[:k]);stable[k].append(same)
      assert not row['certificates'][str(k)+'_full']['cert'][b] or same
    row['diagnostics'].append({'seed':seed,'budget':b,'sampled_ndcg10_mean':float(np.mean(values)),
      'sampled_top_k_stable':{str(k):float(np.mean(v)) for k,v in stable.items()}})
  row['query_seconds']=time.perf_counter()-start;row['process_peak_mib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024
  with output.open('a') as f:f.write(json.dumps(native(row),ensure_ascii=False)+'\n')
  print(ds,phase,qi+1,'/',len(ids),'sec',round(row['query_seconds'],2),'cert_top10',got['full']['cert'].tolist(),flush=True)
  del F,query

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','screen','confirmation']);p.add_argument('--dataset',choices=CONFIG['datasets'],required=True);a=p.parse_args()
 if a.command=='prepare':prepare(a.dataset)
 else:evaluate(a.dataset,a.command)

if __name__=='__main__':main()
