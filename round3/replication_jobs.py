"""Run frozen independent replication commands with at most two CPU jobs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json,subprocess,sys,threading,time

ROOT=Path(__file__).resolve().parent
PRECOMMIT='5fcf816da7d686427f518845c71e682d95626cee'
lock=threading.Lock()
def event(x):
 with lock:
  with (ROOT/'results/replication_execution_events.jsonl').open('a') as f:f.write(json.dumps({'unix_time':time.time(),'preconfirmation_commit':PRECOMMIT,**x})+'\n')
def job(ds):
 output=ROOT/'results'/(ds+'_independent_replication.jsonl')
 if output.exists():raise RuntimeError('Refuse to overwrite confirmation: '+ds)
 event({'event':'start','dataset':ds})
 args=[sys.executable,'-u',str(ROOT/'replication.py'),'run','--dataset',ds]
 with (ROOT/('replication_'+ds+'.log')).open('w') as log:r=subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
 event({'event':'finish','dataset':ds,'exit_code':r.returncode})
 print(ds,'finished',r.returncode,flush=True)
 return r.returncode
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=2) as pool:codes=list(pool.map(job,['scifact','nfcorpus','fiqa']))
 if any(codes):raise SystemExit(1)
