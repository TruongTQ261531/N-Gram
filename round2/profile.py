"""Post-training inference profile in fresh processes; no dataset-loader peak RSS."""
import os
for x in ['OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS']:os.environ[x]='1'
import json,sys,time,resource,subprocess
from pathlib import Path
import numpy as np
from scipy import sparse
from artifact import load_model
from core import ROOT,RES
from lattice import exact_path

def worker(ds):
 en,W,labels=load_model(RES/(ds+'_bolt_model.npz'));texts=json.loads((ROOT/'profile_fixtures'/f'{ds}.json').read_text())
 def infer(text,reset=False):
  if reset:en.words=[];en.index={};en.V=sparse.csr_matrix((0,en.f))
  d=en.encode(text);scores=np.asarray(en.features([d])@W).ravel();y=int(scores.argmax());u,e=en.potentials(W,d,en.tables(W));v=[]
  for c in range(W.shape[1]):
   if c!=y:v.append(exact_path(np.ascontiguousarray(u[:,:,c]-u[:,:,y]),np.ascontiguousarray(e[:,:,:,c]-e[:,:,:,y]),d.costs,3)[0]+W[-1,c]-W[-1,y])
  return y,max(v)<-1e-9
 infer(texts[0]);cold=[];warm=[]
 for s in texts[:50]:
  t=time.perf_counter();infer(s,True);cold.append((time.perf_counter()-t)*1000)
 for s in texts:infer(s)
 for rep in range(3):
  for s in texts:
   t=time.perf_counter();infer(s);warm.append((time.perf_counter()-t)*1000)
 print(json.dumps({'dataset':ds,'model_bytes':(RES/(ds+'_bolt_model.npz')).stat().st_size,'warm_predict_and_certify_p50_ms':float(np.median(warm)),'warm_predict_and_certify_p95_ms':float(np.quantile(warm,.95)),'cold_form_cache_p50_ms':float(np.median(cold)),'cold_form_cache_p95_ms':float(np.quantile(cold,.95)),'warm_measurements':len(warm),'cold_measurements':len(cold),'peak_process_rss_mib':float(next(l.split()[1] for l in Path('/proc/self/status').read_text().splitlines() if l.startswith('VmHWM:')))/1024,'inherited_ru_maxrss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'notes':'Prediction plus exact budget-3 invariance check for predicted class; preloaded model; Numba warm. Peak includes interpreter, dependencies, model, input slice and transformed-token cache. Fresh process per dataset; no training or full-corpus loader in worker. Peak is /proc VmHWM after exec; ru_maxrss is retained separately because it may inherit the parent peak across fork/exec.'}))
if __name__=='__main__':
 if len(sys.argv)>1:worker(sys.argv[1])
 else:
  from run import DS,load
  import pandas as pd
  f=ROOT/'profile_fixtures';f.mkdir(exist_ok=True)
  for ds in DS:
   te=load(ds)[2];(f/(ds+'.json')).write_text(json.dumps(te.head(150).text.tolist()))
  out=[]
  for ds in DS:
   r=subprocess.run([sys.executable,__file__,ds],capture_output=True,text=True,check=True);out.append(json.loads(r.stdout))
  pd.DataFrame(out).to_csv(RES/'profile.csv',index=False)
  (RES/'hardware.json').write_text(json.dumps({'visible_cpus':os.cpu_count(),'model':next((l.split(':',1)[1].strip() for l in Path('/proc/cpuinfo').read_text().splitlines() if l.startswith('model name')),'unknown'),'cpu_quota':Path('/sys/fs/cgroup/cpu.max').read_text().strip()},indent=2))
  print(json.dumps(out,indent=2))
