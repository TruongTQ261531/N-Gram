"""Offline verification of committed arrays/configuration; no corpus download or model fitting."""
from pathlib import Path
import json,hashlib,sys
import numpy as np,pandas as pd
ROOT=Path(__file__).resolve().parent;R=ROOT/'results'
f=json.loads((R/'selection_freeze.json').read_text())
assert hashlib.sha256((R/'selected.json').read_bytes()).hexdigest()==f['selected_sha256']
assert hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest()==f['protocol_sha256']
for name,h in f['source_hashes'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
M=pd.read_csv(R/'metrics.csv').set_index(['dataset','seed','method','budget']);D=pd.read_csv(R/'diagnostics.csv').set_index(['dataset','seed','method','condition']);checks=0;dc=0
for ds in ['UIT-VSFC','UIT-VSMEC','Allocine-FR']:
 z=np.load(R/(ds+'_predictions.npz'),allow_pickle=False);y=z['y'];k=int(y.max()+1);C=z['cert'];assert np.array_equal(C,z['margins'].max(-1)<-1e-9);assert np.all(~C[:,:,1:]|C[:,:,:-1]);assert np.all(~z['loose']|C);assert np.all(~C|z['greedy'])
 for si,seed in enumerate(z['seeds']):
  for mi,method in enumerate(z['methods']):
   p=z['pred'][si,mi];cm=np.bincount(k*y+p,minlength=k*k).reshape(k,k);den=cm.sum(0)+cm.sum(1);f1=np.divide(2*np.diag(cm),den,out=np.zeros(k),where=den>0).mean()
   for bi,b in enumerate(z['budgets']):
    row=M.loc[(ds,int(seed),str(method),int(b))];v=C[si,mi,bi];ba=np.mean([v[y==c].mean() for c in range(k)])
    assert abs(f1-row.macro_f1)<1e-12 and abs(np.mean(y==p)-row.accuracy)<1e-12
    assert abs(v.mean()-row.robust_accuracy)<1e-12 and abs(ba-row.robust_balanced_accuracy)<1e-12
    assert int((z['greedy'][si,mi,bi]&~v).sum())==row.greedy_false_certificates_if_misused;checks+=1
   for di,name in enumerate(['random10','random30','max_allowed_fold']):
    p=z['diagnostic_pred'][si,mi,di];cm=np.bincount(k*y+p,minlength=k*k).reshape(k,k);den=cm.sum(0)+cm.sum(1);ff=np.divide(2*np.diag(cm),den,out=np.zeros(k),where=den>0).mean();row=D.loc[(ds,int(seed),str(method),name)];assert abs(ff-row.macro_f1)<1e-12 and abs(np.mean(p==y)-row.accuracy)<1e-12;dc+=1
 model=np.load(R/(ds+'_bolt_model.npz'),allow_pickle=False);assert np.isfinite(model['W']).all() and np.isfinite(model['idf']).all()
 assert model['W'].shape==(2*len(model['vocab'])+2*int(model['bins'])+1,k)
assert checks==270 and dc==162
if '--skip-checksums' not in sys.argv and (ROOT/'checksums.sha256').exists():
 for line in (ROOT/'checksums.sha256').read_text().splitlines():
  h,n=line.split('  ',1);assert hashlib.sha256((ROOT.parent/n).read_bytes()).hexdigest()==h,n
 print('SHA-256 files verified')
print('Frozen source/config hashes verified; independently reconstructed',checks,'metric rows and',dc,'diagnostic rows')
