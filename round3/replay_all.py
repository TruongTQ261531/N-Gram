from pathlib import Path
import subprocess,sys
R=Path(__file__).resolve().parent
for ds in ['scifact','nfcorpus','fiqa']:
 with (R/('replay_'+ds+'.log')).open('w') as f:
  p=subprocess.run([sys.executable,'-u',str(R/'replay.py'),'--dataset',ds],stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise SystemExit(p.returncode)
 print(ds,'controlled replay complete',flush=True)
