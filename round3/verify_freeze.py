"""Verify frozen source and selection metadata, without loading raw corpora."""
from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parent
f=json.loads((R/'results/confirmation_freeze.json').read_text())
for p,h in f['files'].items():
 actual=hashlib.sha256((R/p).read_bytes()).hexdigest()
 if actual!=h:raise RuntimeError('Frozen file mismatch: '+p)
print('Frozen preconfirmation files verified:',len(f['files']))
