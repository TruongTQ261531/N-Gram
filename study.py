"""CPU experiment. Run protocol before test. No test-based hyperparameter selection."""
import os
for k in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[k]='1'
import json,time,pickle,hashlib,platform,sys,unicodedata,resource
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np,pandas as pd,scipy,sklearn
from scipy import sparse
from scipy.special import rel_entr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.svm import LinearSVC
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import f1_score,accuracy_score
from noise import normalize,fold,corrupt,augment,FAMILIES
ROOT=Path(__file__).resolve().parent
RES=ROOT/'results';RES.mkdir(exist_ok=True)
SEEDS=[17,29,43,71,101]
METHODS=['word','char','svm','folded','concat','aug','uniform','capc','shuffled']
DATASETS=['UIT-VSFC','UIT-VSMEC']
def dump(name,obj):
 (RES/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2))
def load_data(name):
 fs=['UIT-VSFC_train.csv','UIT-VSFC_valid.csv','UIT-VSFC_test.csv'] if name=='UIT-VSFC' else ['train.csv','validation.csv','test.csv']
 frames=[]; original_sizes=[]; dropped_missing=[]
 for f in fs:
  d=pd.read_csv(ROOT/'data'/name/f)
  d=d.rename(columns={'Sentence':'text','Emotion':'label'})
  original_sizes.append(len(d)); dropped_missing.append(int(d[['text','label']].isna().any(axis=1).sum()))
  d=d.dropna(subset=['text','label']).copy()
  assert not d[['text','label']].isna().any().any()
  d['row_id']=np.arange(len(d));d['text']=d.text.map(normalize)
  assert (d.text.str.len()>0).all()
  frames.append(d)
 tr,dv,te=frames
 stats={'file_row_counts':original_sizes,'dropped_missing':dropped_missing,'original_sizes':[len(d) for d in frames], 'class_counts_original':[d.label.value_counts().to_dict() for d in frames], 'exact_duplicate_extra_rows':[int(d.text.duplicated().sum()) for d in frames], 'conflicting_text_groups':[int((d.groupby('text').label.nunique()>1).sum()) for d in frames]}
 stats['overlap_exact']={key:len(set(a.text)&set(b.text)) for key,a,b in [('train_dev',tr,dv),('train_test',tr,te),('dev_test',dv,te)]}
 stats['overlap_folded']={key:len(set(a.text.map(fold))&set(b.text.map(fold))) for key,a,b in [('train_dev',tr,dv),('train_test',tr,te),('dev_test',dv,te)]}
 seen=set(tr.text)|set(dv.text)
 dv=dv[~dv.text.isin(set(tr.text))].drop_duplicates('text').copy()
 te=te[~te.text.isin(seen)].drop_duplicates('text').copy()
 stats['primary_sizes']=[len(tr),len(dv),len(te)]
 assert not(set(tr.text)&set(dv.text) or set(tr.text)&set(te.text) or set(dv.text)&set(te.text))
 enc=LabelEncoder().fit(tr.label)
 return tr,dv,te,enc,stats

def _counts(texts,y,k):
 surface=defaultdict(lambda:np.zeros(k)); families=defaultdict(lambda:np.zeros(k)); forms=defaultdict(set)
 cw=1/np.bincount(y,minlength=k)
 for s,c in zip(texts,y):
  for t in set(s.split()):
   surface[t][c]+=cw[c];families[fold(t)][c]+=cw[c];forms[fold(t)].add(t)
 return surface,families,forms

def reliability(texts,y,k):
 out=np.ones(len(texts)); arr=np.array(texts,dtype=object)
 for train,held in StratifiedKFold(3,shuffle=True,random_state=2026).split(arr,y):
  a,b,forms=_counts(arr[train],y[train],k)
  for idx in held:
   js=[]
   for t in set(texts[idx].split()):
    f=fold(t)
    if t not in a or len(forms.get(f,()))<2:continue
    # Pseudocount is 0.1 times average weighted document contribution.
    smooth=.1/len(train)
    p=a[t]+smooth;q=b[f]+smooth;p/=p.sum();q/=q.sum();m=(p+q)/2
    js.append(float((rel_entr(p,m).sum()+rel_entr(q,m).sum())/(2*np.log(2))))
   out[idx]=np.exp(-4*max(js,default=0))
 assert np.isfinite(out).all() and ((out>0)&(out<=1)).all()
 return out

def vectorizers(tr):
 c=TfidfVectorizer(preprocessor=normalize,lowercase=False,analyzer='char',ngram_range=(2,5),min_df=2,max_features=30000,sublinear_tf=True,dtype=np.float64)
 c.fit(list(tr.text)+[fold(s) for s in tr.text])
 w=TfidfVectorizer(preprocessor=normalize,lowercase=False,ngram_range=(1,2),min_df=2,max_features=30000,sublinear_tf=True,dtype=np.float64)
 w.fit(tr.text)
 return c,w

def matrices(texts,c,w,need_word=True):
 a=c.transform(texts);b=c.transform([fold(s) for s in texts])
 return {'char':a,'folded':b,'concat':sparse.hstack([a,b],format='csr')/np.sqrt(2),'word':w.transform(texts) if need_word else None}

def train_models(tr,c,w,enc,weights,seed,configs):
 y=enc.transform(tr.label);k=len(enc.classes_);n=len(y);Y=np.eye(k)[y]
 bal=n/(k*np.bincount(y));sw=bal[y]
 M=matrices(list(tr.text),c,w)
 augX=c.transform([augment(s,seed) for s in tr.text])
 A=sparse.vstack([M['char'],M['folded'],augX],format='csr')
 Z=np.tile(Y,(3,1));aws=np.tile(sw/3,3)
 D=M['char']-M['folded']
 models={};timing={}
 for method,cf in configs.items():
  t=time.perf_counter()
  if method=='svm':
   model=LinearSVC(C=cf['C'],class_weight='balanced',random_state=seed,dual='auto',tol=1e-4,max_iter=3000).fit(M['char'],y)
  else:
   model=Ridge(alpha=cf['alpha'],fit_intercept=False,solver='lsqr',tol=1e-5,max_iter=500)
   if method in ['aug','uniform','capc','shuffled']:
    XX=A;YY=Z;ss=aws
    if method!='aug':
     r=np.ones(n) if method=='uniform' else weights.copy()
     if method=='shuffled':np.random.default_rng(seed).shuffle(r)
     XX=sparse.vstack([A,D],format='csr');YY=np.vstack([Z,np.zeros((n,k))]);ss=np.r_[aws,cf['lam']*sw*r]
    model.fit(XX,YY,sample_weight=ss)
   else:model.fit(M[method],Y,sample_weight=sw)
  models[method]=model;timing[method]=time.perf_counter()-t
 return models,timing

def pred(method,model,M):
 x=M['char'] if method in ['svm','aug','uniform','capc','shuffled'] else M[method]
 return model.predict(x) if method=='svm' else model.predict(x).argmax(1)
def metric(y,p,k):return float(f1_score(y,p,labels=np.arange(k),average='macro',zero_division=0))
def condition_texts(texts,seed,dev=False):
 if dev:return [('clean',0,texts)]+[(f,.3,[corrupt(s,f,.3,seed) for s in texts]) for f in ['fold','keyboard','repeat','teencode']]
 return [('clean',0,texts),('fullfold',1,[fold(s) for s in texts]),('nfd',0,[unicodedata.normalize('NFD',s) for s in texts])]+[(f,p,[corrupt(s,f,p,seed) for s in texts]) for f in FAMILIES for p in [.1,.2,.3]]

def select():
 all_select={};all_scores=[];audit={}
 for ds in DATASETS:
  print('PREPARE',ds,flush=True)
  tr,dv,te,enc,au=load_data(ds);audit[ds]=au;dump('data_audit.json',audit)
  c,w=vectorizers(tr);r=reliability(list(tr.text),enc.transform(tr.label),len(enc.classes_))
  dump(ds+'_reliability.json',{'min':float(r.min()),'mean':float(r.mean()),'quantiles':np.quantile(r,[0,.1,.5,.9,1]).tolist(),'fraction_below_1':float(np.mean(r<1))})
  devM=[(f,p,matrices(ss,c,w)) for f,p,ss in condition_texts(list(dv.text),9001,True)]
  y=enc.transform(dv.label);k=len(enc.classes_);candidate={m:[] for m in METHODS}
  for a in [1.,10.]:
   for l in [.3,3.]:
    cfg={m:({'C':.5 if a==1 else 2.} if m=='svm' else {'alpha':a,**({'lam':l} if m in ['uniform','capc','shuffled'] else {})}) for m in METHODS if l==.3 or m in ['uniform','capc','shuffled']}
    models,tim=train_models(tr,c,w,enc,r,17,cfg)
    for m,model in models.items():
     vals=[metric(y,pred(m,model,M),k) for f,p,M in devM]
     row=dict(dataset=ds,method=m,config=cfg[m],clean=vals[0],objective=float(np.mean(vals)),cells=vals,fit_seconds=tim[m]);candidate[m].append(row);all_scores.append(row)
  ref=max(candidate['char'],key=lambda v:v['clean'])['clean']
  selected={}
  for m,rows in candidate.items():
   feasible=[z for z in rows if z['clean']>=ref-.01] if m!='svm' else rows
   pool=feasible or rows
   best=max(pool,key=lambda v:v['objective']);selected[m]=best['config'];best['clean_constraint_feasible']=bool(feasible)
   print('SELECT',ds,m,best,flush=True)
  all_select[ds]=selected
  with open(RES/(ds+'_prepared.pkl'),'wb') as f:pickle.dump((c,w,r,enc),f)
 dump('dev_search.json',all_scores);dump('selected.json',all_select)
 dump('selection_freeze.json',{'selected_sha256':hashlib.sha256((RES/'selected.json').read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest(),'test_predictions_exist':list(RES.glob('*predictions.npz'))!=[],'unix_time':time.time()})

def evaluate():
 assert (RES/'selection_freeze.json').exists()
 configs=json.loads((RES/'selected.json').read_text());rows=[];eff=[];repro=[]
 for ds in DATASETS:
  tr,dv,te,enc,au=load_data(ds)
  with open(RES/(ds+'_prepared.pkl'),'rb') as f:c,w,r,enc=pickle.load(f)
  yt=enc.transform(te.label);k=len(enc.classes_);texts=list(te.text)
  preds=np.zeros((len(SEEDS),27,len(METHODS),len(te)),dtype=np.int16);metadata=[];corruption_audit=[]
  seed17models=None
  for si,seed in enumerate(SEEDS):
   print('FIT',ds,seed,flush=True)
   models,tim=train_models(tr,c,w,enc,r,seed,configs[ds])
   if si==0:seed17models=models
   for ci,(family,p,ss) in enumerate(condition_texts(texts,100000+seed)):
    M=matrices(ss,c,w)
    if si==0:metadata.append({'family':family,'severity':p})
    changed=[a!=b for a,b in zip(texts,ss)]
    corruption_audit.append(dict(dataset=ds,seed=seed,family=family,severity=p,changed_sentence_fraction=float(np.mean(changed)),changed_token_fraction=float(np.mean([sum(x!=z for x,z in zip(a.split(),b.split()))/max(1,len(a.split())) for a,b in zip(texts,ss)])) if family!='whitespace' else None, mean_original_tokens=float(np.mean([len(s.split()) for s in texts])),mean_noisy_tokens=float(np.mean([len(s.split()) for s in ss]))))
    for mi,m in enumerate(METHODS):
     pp=pred(m,models[m],M);preds[si,ci,mi]=pp
     fvec=f1_score(yt,pp,labels=np.arange(k),average=None,zero_division=0)
     rows.append(dict(dataset=ds,seed=seed,method=m,family=family,severity=p,n_test=len(te),macro_f1=float(fvec.mean()),accuracy=float(accuracy_score(yt,pp)),per_class_f1=json.dumps(fvec.tolist()),fit_seconds=tim[m]))
   for m in METHODS:
    bundle={'model':models[m],'char_vectorizer':c if m!='word' else None,'word_vectorizer':w if m=='word' else None,'labels':enc.classes_.tolist(),'method':m,'config':configs[ds][m]}
    blob=pickle.dumps(bundle,protocol=5)
    if si==0:
     (RES/(ds+'_'+m+'_seed17.pkl')).write_bytes(blob)
     times=[]
     for rep in range(3):
      for s in texts[:150]:
       t=time.perf_counter();ss=[normalize(s)];mm={};key='char' if m in ['svm','aug','uniform','capc','shuffled'] else m
       if key=='word':mm[key]=w.transform(ss)
       elif key=='folded':mm[key]=c.transform([fold(ss[0])])
       elif key=='concat':mm[key]=sparse.hstack([c.transform(ss),c.transform([fold(ss[0])])],format='csr')/np.sqrt(2)
       else:mm[key]=c.transform(ss)
       pred(m,models[m],mm);times.append((time.perf_counter()-t)*1000)
     eff.append(dict(dataset=ds,method=m,serialized_bytes=len(blob),latency_p50_ms=float(np.median(times)),latency_p95_ms=float(np.quantile(times,.95)),latency_n=len(times),fit_seconds=tim[m],note='method-specific transform plus normalize and predict; shared feature prep and augmentation excluded from fit_seconds'))
   print('DONE',ds,seed,flush=True)
  # True repeat fit, not simply reuse predictions.
  repeated,_=train_models(tr,c,w,enc,r,17,configs[ds]);cleanM=matrices(texts,c,w)
  for mi,m in enumerate(METHODS):
   p=pred(m,repeated[m],cleanM);same=bool(np.array_equal(p,preds[0,0,mi]));assert same
   repro.append(dict(dataset=ds,method=m,seed=17,repeat_predictions_identical=same))
  np.savez_compressed(RES/(ds+'_predictions.npz'),pred=preds,y=yt,row_id=te.row_id.to_numpy(),methods=np.array(METHODS),seeds=np.array(SEEDS))
  dump(ds+'_conditions.json',metadata);dump(ds+'_corruptions.json',corruption_audit)
  # Export references and examples for independent human review, not evaluated as human-verified.
  examples=[]
  for f in FAMILIES:
   for _,row in te.head(15).iterrows():examples.append(dict(row_id=int(row.row_id),family=f,severity=.3,original=row.text,noisy=corrupt(row.text,f,.3,100017),label=row.label,human_verified='NO'))
  pd.DataFrame(examples).to_csv(RES/(ds+'_noise_review.csv'),index=False)
 pd.DataFrame(rows).to_csv(RES/'metrics.csv',index=False);pd.DataFrame(eff).to_csv(RES/'efficiency.csv',index=False)
 dump('reproducibility.json',repro)
 dump('runtime.json',{'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'pandas':pd.__version__,'platform':platform.platform(),'cpu_count':os.cpu_count(),'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'threads':1,'finished_unix':time.time()})
if __name__=='__main__':
 if sys.argv[1]=='select':select()
 elif sys.argv[1]=='evaluate':evaluate()
 else:raise ValueError('choose select or evaluate')
