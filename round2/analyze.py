import os
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['MPLCONFIGDIR']='/tmp/bolt-mpl';os.environ['XDG_CACHE_HOME']='/tmp/bolt-xdg'
import json
import numpy as np,pandas as pd
from core import RES
from run import DS,METHODS
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
m=pd.read_csv(RES/'metrics.csv');summary=m.groupby(['dataset','method','budget']).agg(clean_f1=('macro_f1','mean'),accuracy=('accuracy','mean'),robust_accuracy=('robust_accuracy','mean'),robust_balanced_accuracy=('robust_balanced_accuracy','mean'),loose_accuracy=('factor_cert_accuracy','mean'),greedy_survival=('greedy_survival_accuracy','mean'),greedy_missed=('greedy_false_certificates_if_misused','mean')).reset_index();summary.to_csv(RES/'summary.csv',index=False)
bs=[]
for ds in DS:
 z=np.load(RES/(ds+'_predictions.npz'));C=z['cert'];y=z['y'];n=len(y);k=int(y.max()+1);r=np.random.default_rng(20261027)
 # Mean over training seeds first: bootstrap still resamples each original jointly.
 A=C.mean(0).transpose(2,0,1).reshape(n,-1)
 BB=[]
 for i in range(20):
  weights=r.multinomial(n,np.full(n,1/n),size=100).astype(float)
  # Balanced robust accuracy with resampled class denominators.
  out=np.zeros((100,6*5))
  for c in range(k):
   ix=(y==c);wc=weights[:,ix];out+=(wc@A[ix])/np.maximum(1,wc.sum(1))[:,None]/k
  BB.append(out.reshape(100,6,5))
 B=np.concatenate(BB)
 for base in ['clean','canonical','random','greedy','unary']:
  for bi,b in enumerate([0,1,2,3,5]):
   delta=B[:,5,bi]-B[:,METHODS.index(base),bi];lo,hi=np.quantile(delta,[.025,.975])
   ss=summary[(summary.dataset==ds)&(summary.budget==b)].set_index('method')
   bs.append({'dataset':ds,'contrast':'bolt - '+base,'budget':b,'balanced_robust_delta':float(ss.loc['bolt','robust_balanced_accuracy']-ss.loc[base,'robust_balanced_accuracy']),'ci_low':float(lo),'ci_high':float(hi),'bootstrap':2000})
 np.savez_compressed(RES/(ds+'_bootstrap.npz'),values=B)
pd.DataFrame(bs).to_csv(RES/'paired_bootstrap.csv',index=False)
fig,axs=plt.subplots(1,3,figsize=(15,4))
for ax,ds in zip(axs,DS):
 for method in METHODS:
  d=summary[(summary.dataset==ds)&(summary.method==method)]
  ax.plot(d.budget,d.robust_balanced_accuracy*100,marker='o',label=method,linewidth=2 if method=='bolt' else 1)
 ax.set_title(ds);ax.set_xlabel('Budget (changed NFC codepoints)');ax.set_ylabel('Exact balanced robust accuracy (%)');ax.grid(alpha=.2)
axs[-1].legend(fontsize=8);fig.tight_layout();fig.savefig(RES/'robustness_curve.png',dpi=180)
print(summary[summary.budget==3].to_string(index=False));print(pd.DataFrame(bs)[lambda d:d.budget==3].to_string(index=False))
