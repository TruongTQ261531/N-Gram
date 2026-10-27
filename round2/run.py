import os
for k0 in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k0]='1'
import json,pickle,time,hashlib,sys,platform
from pathlib import Path
import numpy as np,pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from core import ROOT,RES,Encoder,train,evaluate,score_metrics,normalize,fold
from study import load_data
DS=['UIT-VSFC','UIT-VSMEC','Allocine-FR'];METHODS=['clean','canonical','random','greedy','unary','bolt'];SEEDS=[17,29,43]
def dump(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False))
def subset(d,n,seed=20261027):
 if len(d)<=n:return d.copy()
 ix,_=train_test_split(np.arange(len(d)),train_size=n,stratify=d.label,random_state=seed)
 return d.iloc[np.sort(ix)].copy()
def load(ds):
 if ds!='Allocine-FR':tr,dv,te,le,old=load_data(ds)
 else:
  fr=[]
  for sp,n in [('train',5000),('validation',1000),('test',2000)]:
   d=pd.read_parquet(ROOT/'data/fr'/f'{sp}.parquet').rename(columns={'review':'text'});d['row_id']=np.arange(len(d));fr.append(subset(d,n))
  tr,dv,te=fr;le=LabelEncoder().fit(tr.label);old={}
 before=[len(z) for z in [tr,dv,te]]
 for d in [tr,dv,te]:d['text']=d.text.map(lambda s:' '.join(normalize(s).split()[:128]))
 seen=set(tr.text)|set(dv.text)
 dv=dv[~dv.text.isin(set(tr.text))].drop_duplicates('text').copy()
 te=te[~te.text.isin(seen)].drop_duplicates('text').copy()
 audit={'before_new_cleaning':before,'sizes':[len(z) for z in [tr,dv,te]],'labels':le.classes_.tolist(),'source_original_audit':old,'test_status':'independent confirmation' if ds=='Allocine-FR' else 'exploratory: test scores previously inspected in CAPC'}
 assert not(set(tr.text)&set(dv.text) or set(tr.text)&set(te.text) or set(dv.text)&set(te.text))
 return tr,dv,te,le,audit

def balanced(y,cert):return float(np.mean([cert[y==c].mean() for c in np.unique(y)]))
def valstats(enc,docs,y,W,k):
 ev=evaluate(enc,docs,y,W,budgets=(0,1,3),diagnose=False);met=score_metrics(y,ev['pred'],k)
 b=[balanced(y,e) for e in ev['cert']];met['robust_balanced']=b;met['robust_accuracy']=ev['cert'].mean(1).tolist();met['objective']=.5*met['macro_f1']+.25*b[1]+.25*b[2]
 return met

def prepare():
 for ds in DS:
  tr,dv,te,le,au=load(ds);print('PREPARE',ds,au['sizes'],flush=True)
  en=Encoder(list(tr.text));train_docs=[en.encode(r.text,r.row_id) for r in tr.itertuples()];dev_docs=[en.encode(r.text,r.row_id) for r in dv.itertuples()]
  # Test encoder transforms are intentionally deferred until selection is frozen.
  y=le.transform(tr.label);yd=le.transform(dv.label)
  ix=subset(tr,2000).index;positions=tr.index.get_indexer(ix)
  with open(RES/(ds+'_prepared.pkl'),'wb') as f:pickle.dump((en,train_docs,y,dev_docs,yd,le,positions),f)
  dump(RES/(ds+'_audit.json'),au)
  dump(RES/(ds+'_split_ids.json'),{'train':tr.row_id.tolist(),'dev':dv.row_id.tolist(),'test':te.row_id.tolist(),'screen_train_positions':positions.tolist()})

def select():
 selected={};rows=[]
 for ds in DS:
  with open(RES/(ds+'_prepared.pkl'),'rb') as f:en,td,y,dd,yd,le,ix=pickle.load(f)
  tiny=[td[i] for i in ix];yt=y[ix];k=len(le.classes_);candidates={m:[] for m in METHODS}
  for m in METHODS:
   for alpha in [.0001,.001]:
    for eta in ([.3,.7] if m=='bolt' else [.7]):
     print('SCREEN',ds,m,alpha,eta,flush=True)
     W,log=train(en,tiny,yt,k,alpha,eta,17,m,rounds=4,maxiter=30,budget=3)
     metrics=valstats(en,dd,yd,W,k)
     row={'dataset':ds,'method':m,'alpha':alpha,'eta':eta,'metrics':metrics,'training':log,'screen_train_n':len(tiny)};rows.append(row);candidates[m].append(row)
     dump(RES/'dev_search.json',rows)
  ref=max(z['metrics']['macro_f1'] for z in candidates['clean'])
  selected[ds]={}
  for m,rr in candidates.items():
   feasible=[r for r in rr if r['metrics']['macro_f1']>=ref-.02];best=max(feasible or rr,key=lambda v:v['metrics']['objective'])
   selected[ds][m]={'alpha':best['alpha'],'eta':best['eta'],'clean_constraint_feasible':bool(feasible),'screen_validation':best['metrics']}
   print('SELECT',ds,m,selected[ds][m],flush=True)
  dump(RES/'selected.json',selected)
 dump(RES/'selection_freeze.json',{'selected_sha256':hashlib.sha256((RES/'selected.json').read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),'source_hashes':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['core.py','lattice.py','run.py']},'unix_time':time.time(),'french_test_predictions_exist':(RES/'Allocine-FR_predictions.npz').exists()})

def final():
 selected=json.loads((RES/'selected.json').read_text());fr=json.loads((RES/'selection_freeze.json').read_text());assert hashlib.sha256((RES/'selected.json').read_bytes()).hexdigest()==fr['selected_sha256']
 rows=[];fitlogs=[];diag=[];diagnostic_rows=[]
 for ds in DS:
  with open(RES/(ds+'_prepared.pkl'),'rb') as f:en,td,y,dd,yd,le,ix=pickle.load(f)
  _,_,te,_,_=load(ds);testdocs=[en.encode(r.text,r.row_id) for r in te.itertuples()];yy=le.transform(te.label);k=len(le.classes_);n=len(te)
  P=np.zeros((3,6,n),np.int16);C=np.zeros((3,6,5,n),bool);M=np.zeros((3,6,5,n,k));L=np.zeros_like(C);G=np.zeros_like(C);PD=np.zeros((3,6,3,n),np.int16)
  repeat=None
  for si,seed in enumerate(SEEDS):
   rng=np.random.default_rng(100000+seed);dpaths=[]
   for rate in [.1,.3,1.]:
    paths=[]
    for d in testdocs:
     z=np.zeros(len(d.ids),np.int16)
     for ti in range(len(z)):
      valid=np.where(d.costs[ti]<100000)[0]
      if rate==1.:
       match=[v for v in valid if en.words[d.ids[ti,v]]==fold(d.tokens[ti])]
       z[ti]=match[0] if match else 0
      elif rng.random()<rate and len(valid)>1:z[ti]=rng.choice(valid[1:])
     paths.append(z)
    dpaths.append(paths)
   dmat=[en.features(testdocs,ps) for ps in dpaths]
   for mi,m in enumerate(METHODS):
    cf=selected[ds][m];print('FIT',ds,seed,m,flush=True)
    W,log=train(en,td,y,k,cf['alpha'],cf['eta'],seed,m,rounds=6,maxiter=50,budget=3)
    ev=evaluate(en,testdocs,yy,W);P[si,mi]=ev['pred'];C[si,mi]=ev['cert'];M[si,mi]=ev['margins'];L[si,mi]=ev['loose_cert'];G[si,mi]=ev['greedy_survives']
    met=score_metrics(yy,ev['pred'],k)
    for di,name in enumerate(['random10','random30','max_allowed_fold']):
     pp=(dmat[di]@W).argmax(1);PD[si,mi,di]=pp
     diagnostic_rows.append({'dataset':ds,'seed':seed,'method':m,'condition':name,**score_metrics(yy,pp,k)})
    if m=='bolt' and seed==17:
     from artifact import save_model
     save_model(RES/(ds+'_bolt_model.npz'),en,W,le.classes_)
    for bi,b in enumerate([0,1,2,3,5]):
     rows.append({'dataset':ds,'seed':seed,'method':m,'budget':b,'n':n,**met,'robust_accuracy':float(ev['cert'][bi].mean()),'robust_balanced_accuracy':balanced(yy,ev['cert'][bi]),'factor_cert_accuracy':float(ev['loose_cert'][bi].mean()),'greedy_survival_accuracy':float(ev['greedy_survives'][bi].mean()),'greedy_false_certificates_if_misused':int(np.sum(ev['greedy_survives'][bi]&~ev['cert'][bi])),'training_seconds':log['seconds'],'oracle_eval_seconds':ev['seconds']})
    fitlogs.append({'dataset':ds,**log});dump(RES/'training_logs.json',fitlogs)
    if seed==17:
     with open(RES/(ds+'_'+m+'_seed17.pkl'),'wb') as f:pickle.dump((en,W),f)
    print('DONE',ds,seed,m,'clean',round(met['macro_f1'],4),'robust@3',round(ev['cert'][3].mean(),4),flush=True)
   pd.DataFrame(rows).to_csv(RES/'metrics.csv',index=False)
  # True repeat of proposed model on each task; exact weights/predictions compared.
  cf=selected[ds]['bolt'];W2,lg=train(en,td,y,k,cf['alpha'],cf['eta'],17,'bolt',rounds=6,maxiter=50,budget=3)
  with open(RES/(ds+'_bolt_seed17.pkl'),'rb') as f:_,W1=pickle.load(f)
  exact=bool(np.array_equal(W1,W2));predsame=bool(np.array_equal((en.features(testdocs)@W2).argmax(1),P[0,5]));assert predsame
  diag.append({'dataset':ds,'seed':17,'weights_bitwise_equal':exact,'predictions_identical':predsame});dump(RES/'repeat_fit.json',diag)
  np.savez_compressed(RES/(ds+'_predictions.npz'),pred=P,diagnostic_pred=PD,cert=C,margins=M,loose=L,greedy=G,y=yy,row_ids=te.row_id.to_numpy(),methods=np.array(METHODS),seeds=np.array(SEEDS),budgets=np.array([0,1,2,3,5]))
 pd.DataFrame(diagnostic_rows).to_csv(RES/'diagnostics.csv',index=False)
 pd.DataFrame(rows).to_csv(RES/'metrics.csv',index=False);dump(RES/'runtime.json',{'python':sys.version,'platform':platform.platform(),'threads':1,'finished':time.time()})
if __name__=='__main__':{'prepare':prepare,'select':select,'final':final}[sys.argv[1]]()
