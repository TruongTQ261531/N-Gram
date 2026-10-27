"""Isolated-process CPU profile; run only AFTER training has completed."""
import os
for x in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[x]='1'
import sys,json,time,resource,pickle,subprocess
from pathlib import Path
import numpy as np,pandas as pd
from scipy import sparse
from noise import normalize,fold
from study import RES,ROOT,DATASETS,METHODS,load_data

def rss_mib():return int(Path('/proc/self/statm').read_text().split()[1])*os.sysconf('SC_PAGE_SIZE')/(1024**2)
def worker(ds,m):
 _,_,te,_,_=load_data(ds);ss=list(te.text);baseline=rss_mib()
 with open(RES/(ds+'_'+m+'_seed17.pkl'),'rb') as f:b=pickle.load(f)
 model=b['model'];v=b['word_vectorizer'] if m=='word' else b['char_vectorizer'];loaded=rss_mib()
 def predict(texts):
  xs=[normalize(t) for t in texts]
  if m=='folded':X=v.transform([fold(t) for t in xs])
  elif m=='concat':X=sparse.hstack([v.transform(xs),v.transform([fold(t) for t in xs])],format='csr')/np.sqrt(2)
  else:X=v.transform(xs)
  scores=model.predict(X)
  return scores if m=='svm' else scores.argmax(1)
 predict(ss[:32]);times=[]
 for rep in range(3):
  for s in ss[:150]:
   t=time.perf_counter();predict([s]);times.append(time.perf_counter()-t)
 batch=ss[:min(512,len(ss))];bt=[]
 for _ in range(5):
  t=time.perf_counter();predict(batch);bt.append(time.perf_counter()-t)
 print(json.dumps({'dataset':ds,'method':m,'baseline_process_rss_mib':baseline,'model_loaded_process_rss_mib':loaded,'model_load_rss_increment_mib':loaded-baseline,'peak_process_rss_mib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,'batch1_p50_ms':float(np.median(times)*1000),'batch1_p95_ms':float(np.quantile(times,.95)*1000),'batch1_measurements':len(times),'batch_size':len(batch),'batch_throughput_docs_s':len(batch)/float(np.median(bt)),'batch_repeats':5,'threads':1,'serialized_bytes':(RES/(ds+'_'+m+'_seed17.pkl')).stat().st_size,'text_lengths_chars_mean':float(np.mean([len(s) for s in ss[:150]]))}))
if __name__=='__main__':
 if len(sys.argv)==3:worker(*sys.argv[1:])
 else:
  rows=[]
  for ds in DATASETS:
   for m in METHODS:
    p=subprocess.run([sys.executable,__file__,ds,m],capture_output=True,text=True,check=True);rows.append(json.loads(p.stdout))
  pd.DataFrame(rows).to_csv(RES/'isolated_efficiency.csv',index=False)
  (RES/'hardware.json').write_text(json.dumps({'cpuinfo':next((l.split(':',1)[1].strip() for l in Path('/proc/cpuinfo').read_text().splitlines() if l.startswith('model name')),'unknown'),'visible_cpus':os.cpu_count(),'notes':'Container-visible CPU. No clock/governor or physical host isolation guarantee. Peak RSS includes interpreter, imports, data slice, model and inference working set. Values are not attributable solely to model tensors.'},indent=2))
  print(pd.DataFrame(rows).to_string(index=False))
