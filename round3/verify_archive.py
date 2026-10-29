"""Verify this complete released archive without downloading corpora."""
from pathlib import Path
import hashlib,subprocess,sys
R=Path(__file__).resolve().parent
def main():
 manifest=R/'checksums.sha256'
 if not manifest.exists():raise RuntimeError('Release checksum manifest missing')
 count=0
 for line in manifest.read_text().splitlines():
  h,p=line.split('  ',1);assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p;count+=1
 print('Round 3 archive checksums:',count,flush=True)
 for script in ['verify_recorded.py','verify_predictions.py','verify_replication.py']:
  subprocess.run([sys.executable,str(R/script)],cwd=R,check=True)
 print('Recorded evidence verified. Numerical-library assumptions, new-corpus generalization, originality and journal acceptance require separate assessment.',flush=True)
if __name__=='__main__':main()
