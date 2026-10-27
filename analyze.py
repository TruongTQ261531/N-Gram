"""Audit and aggregate every run; paired document-cluster bootstrap, 2000 draws."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['MPLCONFIGDIR']='/tmp/ngram-mpl'
import json,hashlib,time
from pathlib import Path
import numpy as np,pandas as pd
from scipy import sparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from study import ROOT,RES,METHODS,SEEDS,DATASETS,load_data

def mf(conf):
 # Last dimensions are true class, predicted class.
 tp=np.diagonal(conf,axis1=-2,axis2=-1);den=conf.sum(-1)+conf.sum(-2)
 return np.divide(2*tp,den,out=np.zeros_like(tp,dtype=float),where=den>0).mean(-1)

def main():
 df=pd.read_csv(RES/'metrics.csv');assert len(df)==2*5*27*9;assert not df.isna().drop(columns=['per_class_f1'],errors='ignore').any().any()
 aggregates=[];bootrows=[];robustness=[]
 dev=json.loads((RES/'dev_search.json').read_text());sel=json.loads((RES/'selected.json').read_text())
 for ds in DATASETS:
  z=np.load(RES/(ds+'_predictions.npz'));p=z['pred'];y=z['y'];n=len(y);k=int(y.max()+1)
  assert p.shape==(5,27,9,n);assert np.array_equal(p[:,0],p[:,2]),'NFC/NFD must match'
  _,_,te,_,_=load_data(ds);assert np.array_equal(te.row_id,z['row_id'])
  for m in METHODS:
   d=df[(df.dataset==ds)&(df.method==m)];noisy=d[d.family.isin(['fold','tone','keyboard','delete','swap','repeat','whitespace','teencode'])]
   seed_means=noisy.groupby('seed').macro_f1.mean()
   aggregates.append(dict(dataset=ds,method=m,clean_f1=d[d.family=='clean'].macro_f1.mean(),noise_mean_f1=noisy.macro_f1.mean(),noise_seed_sd=seed_means.std(ddof=1),seen_family_mean_f1=noisy[noisy.family.isin(['fold','keyboard','repeat','teencode'])].macro_f1.mean(),heldout_family_mean_f1=noisy[noisy.family.isin(['tone','delete','swap','whitespace'])].macro_f1.mean(),worst_cell_f1=noisy.groupby(['family','severity']).macro_f1.mean().min(),fullfold_f1=d[d.family=='fullfold'].macro_f1.mean()))
  # baseline comparator chosen by DEVELOPMENT objective only (no candidate / controls).
  base=['word','char','svm','folded','concat','aug']
  dv=[r for r in dev if r['dataset']==ds and r['method'] in base and r['config']==sel[ds][r['method']]]
  bestdev=max(dv,key=lambda r:r['objective'])['method']
  print('BOOT',ds,'dev baseline',bestdev,flush=True)
  # Flatten seed x condition x method, one sparse confusion-cell contribution per document/trial.
  pp=p[:,3:,:,:].reshape(-1,n).T;trials=pp.shape[1]
  cols=(np.arange(trials)[None,:]*k*k+y[:,None]*k+pp).ravel()
  rr=np.repeat(np.arange(n),trials)
  C=sparse.csr_matrix((np.ones(len(cols),dtype=np.float64),(rr,cols)),shape=(n,trials*k*k))
  rng=np.random.default_rng(20261027);boot=[]
  for start in range(0,2000,50):
   W=rng.multinomial(n,np.full(n,1/n),size=50).astype(float)
   conf=(C.T@W.T).T.reshape(50,5,24,9,k,k)
   boot.append(mf(conf).mean((1,2)))
  B=np.concatenate(boot,axis=0)
  for mi,m in enumerate(METHODS):
   for row in aggregates:
    if row['dataset']==ds and row['method']==m:
     row['noise_ci_low'],row['noise_ci_high']=[float(v) for v in np.quantile(B[:,mi],[.025,.975])]
  a=pd.DataFrame(aggregates);d=a[a.dataset==ds].set_index('method')
  for other in sorted(set(['char','aug','uniform','shuffled',bestdev])):
   delta=B[:,METHODS.index('capc')]-B[:,METHODS.index(other)]
   lo,hi=np.quantile(delta,[.025,.975]);bootrows.append(dict(dataset=ds,contrast='capc - '+other,delta=float(d.loc['capc','noise_mean_f1']-d.loc[other,'noise_mean_f1']),ci_low=float(lo),ci_high=float(hi),bootstrap_n=2000,development_best_baseline=bestdev,inference='paired document bootstrap; training/noise runs averaged; conditional on fitted runs'))
  # Canonical-key train-overlap removal is a sensitivity analysis, not posthoc tuning.
  tr,dv0,te0,enc,_=load_data(ds);trainfold=set(tr.text.map(__import__('noise').fold));keep=~te0.text.map(__import__('noise').fold).isin(trainfold).to_numpy()
  for mi,m in enumerate(METHODS):
   vals=[]
   for si in range(5):
    for ci in range(3,27):
     cm=np.bincount(k*y[keep]+p[si,ci,mi,keep],minlength=k*k).reshape(k,k);vals.append(mf(cm))
   robustness.append(dict(dataset=ds,method=m,n_after_fold_overlap_removal=int(keep.sum()),n_removed=int((~keep).sum()),noise_mean_f1=float(np.mean(vals))))
  # Per-seed diagnostics, all family means and all deltas retained in metrics.csv.
  np.savez_compressed(RES/(ds+'_bootstrap_means.npz'),values=B,methods=np.array(METHODS))
 df.groupby(['dataset','method','family','severity'])[['macro_f1','accuracy']].agg(['mean','std']).to_csv(RES/'family_summary.csv')
 pd.DataFrame(aggregates).to_csv(RES/'summary.csv',index=False)
 pd.DataFrame(bootrows).to_csv(RES/'paired_bootstrap.csv',index=False)
 pd.DataFrame(robustness).to_csv(RES/'fold_overlap_sensitivity.csv',index=False)
 S=pd.DataFrame(aggregates)
 fig,axs=plt.subplots(1,2,figsize=(12,4.8))
 for ax,ds in zip(axs,DATASETS):
  ss=S[S.dataset==ds];ax.barh(ss.method,ss.noise_mean_f1*100,xerr=np.maximum(0,np.vstack([ss.noise_mean_f1-ss.noise_ci_low,ss.noise_ci_high-ss.noise_mean_f1]))*100,capsize=2,color=['#dc702f' if m=='capc' else '#28678b' for m in ss.method]);ax.set_title(ds+' | synthetic noise');ax.set_xlabel('Macro F1 (mean over 24 conditions and 5 runs)');ax.set_xlim(0,100);ax.grid(axis='x',alpha=.2)
 fig.tight_layout();fig.savefig(RES/'robustness.png',dpi=180);plt.close(fig)
 json.dump({'metric_rows':len(df),'predictions':int(sum(np.load(RES/(ds+'_predictions.npz'))['pred'].size for ds in DATASETS)),'all_27_conditions':True,'nfd_identical_to_clean':True,'training_repeats':18,'bootstrap_replicates':2000},open(RES/'verification.json','w'),indent=2)
 print(S.to_string(index=False),flush=True);print(pd.DataFrame(bootrows).to_string(index=False),flush=True)
if __name__=='__main__':main()
