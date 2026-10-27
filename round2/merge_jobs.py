"""Merge isolated executions of the unchanged frozen final protocol."""
import json,shutil,sys
from pathlib import Path
import numpy as np,pandas as pd
from core import RES,ROOT
from run import DS,METHODS,SEEDS
metrics=[];logs=[];repeats=[];diagnostics=[]
for ds in DS:
 src=RES if ds=='UIT-VSFC' else ROOT/'jobs'/ds
 assert (src/(ds+'_predictions.npz')).exists(),ds
 if src!=RES:
  for f in src.iterdir():
   if f.name.startswith(ds+'_') and not f.is_symlink():shutil.copy2(f,RES/f.name)
 m=pd.read_csv(src/'metrics.csv');metrics.append(m[m.dataset==ds])
 logs.extend(x for x in json.loads((src/'training_logs.json').read_text()) if x['dataset']==ds)
 repeats.extend(x for x in json.loads((src/'repeat_fit.json').read_text()) if x['dataset']==ds)
 z=np.load(src/(ds+'_predictions.npz'));y=z['y'];k=int(y.max()+1)
 # VSFC was stopped after its complete arrays/re-fit; reconstruct diagnostics from stored outputs.
 for si,seed in enumerate(SEEDS):
  for mi,method in enumerate(METHODS):
   for ci,condition in enumerate(['random10','random30','max_allowed_fold']):
    p=z['diagnostic_pred'][si,mi,ci];cm=np.bincount(k*y+p,minlength=k*k).reshape(k,k);den=cm.sum(0)+cm.sum(1);f=np.divide(2*np.diag(cm),den,out=np.zeros(k),where=den>0).mean()
    diagnostics.append(dict(dataset=ds,seed=seed,method=method,condition=condition,macro_f1=float(f),accuracy=float(np.mean(y==p))))
pd.concat(metrics,ignore_index=True).to_csv(RES/'metrics.csv',index=False);pd.DataFrame(diagnostics).to_csv(RES/'diagnostics.csv',index=False)
(RES/'training_logs.json').write_text(json.dumps(logs,indent=2));(RES/'repeat_fit.json').write_text(json.dumps(repeats,indent=2))
(RES/'orchestration.json').write_text(json.dumps({'numerical_threads_per_fit':1,'cpu_quota_cores':2,'execution':'VSFC sequential original final loop; VSMEC and French isolated dataset jobs using the same run.final function, selected config and seeds. Parent stopped after complete VSFC artifacts to avoid duplicate VSMEC. At most two numerical jobs concurrent.','timing_limitation':'Training wall times may reflect resource competition; no controlled per-model training-speed ranking claimed. Inference is profiled after training finishes.','completed_final_fits':54,'completed_repeat_fits':3,'development_fits':42},indent=2))
print('Merged:',len(pd.concat(metrics)),'metric rows,',len(diagnostics),'diagnostics,',len(logs),'final training logs,',len(repeats),'repeat fits')
