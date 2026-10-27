"""Wait for isolated jobs, then run read-only/reconstruction audits sequentially."""
import time,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent

def wait_file(p):
 start=time.monotonic()
 while not p.exists():
  if time.monotonic()-start>5400:raise TimeoutError(str(p))
  time.sleep(2)
def call(script,log):
 print('RUN',script,flush=True)
 with open(P/log,'w') as f:subprocess.run([sys.executable,str(P/script)],stdout=f,stderr=subprocess.STDOUT,check=True)
 print('PASS',script,flush=True)
wait_file(P/'jobs/UIT-VSMEC/runtime.json')
call('dual_audit.py','dual_audit.log')
wait_file(P/'jobs/Allocine-FR/runtime.json')
for script,log in [('merge_jobs.py','merge.log'),('verify.py','verification.log'),('audit_milp.py','milp.log'),('analyze.py','analysis.log'),('audit_optimization.py','optimization.log'),('profile.py','profile.log')]:call(script,log)
(P/'POST_DONE').write_text('All reconstruction, oracle, optimization and isolated profile audits completed.\n')
