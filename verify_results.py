"""Independently reconstruct all reported F1/accuracy values from prediction arrays."""
import json,hashlib,sys
from pathlib import Path
import numpy as np,pandas as pd
root=Path(__file__).resolve().parent;res=root/'results'
freeze=json.loads((res/'selection_freeze.json').read_text())
assert hashlib.sha256((res/'selected.json').read_bytes()).hexdigest()==freeze['selected_sha256']
assert hashlib.sha256((root/'PROTOCOL.md').read_bytes()).hexdigest()==freeze['protocol_sha256']
print('Frozen configuration/protocol hashes match')
df=pd.read_csv(res/'metrics.csv');checked=0
for ds in ['UIT-VSFC','UIT-VSMEC']:
 z=np.load(res/(ds+'_predictions.npz'));y=z['y'];k=int(y.max()+1)
 cond=json.loads((res/(ds+'_conditions.json')).read_text())
 for si,seed in enumerate(z['seeds']):
  for ci,c in enumerate(cond):
   for mi,m in enumerate(z['methods']):
    p=z['pred'][si,ci,mi];cm=np.bincount(k*y+p,minlength=k*k).reshape(k,k)
    den=cm.sum(0)+cm.sum(1);v=np.divide(2*np.diag(cm),den,out=np.zeros(k),where=den>0)
    row=df[(df.dataset==ds)&(df.seed==seed)&(df.method==m)&(df.family==c['family'])&np.isclose(df.severity,c['severity'])]
    assert len(row)==1
    assert abs(v.mean()-row.iloc[0].macro_f1)<1e-12
    assert abs(np.mean(y==p)-row.iloc[0].accuracy)<1e-12
    assert np.allclose(v,json.loads(row.iloc[0].per_class_f1),atol=1e-12)
    checked+=1
print('Independent reconstruction passed:',checked,'metric rows')
assert checked==2430
p=res/'checksums.sha256'
if p.exists() and '--metrics-only' not in sys.argv:
 for line in p.read_text().splitlines():
  h,name=line.split('  ',1);q=root/name
  assert hashlib.sha256(q.read_bytes()).hexdigest()==h,name
 print('SHA-256 integrity passed')
