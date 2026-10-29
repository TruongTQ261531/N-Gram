from pathlib import Path
import hashlib,json,platform,sys,time
from core import ROOT,Index
from run import CONFIG,RES,CACHE

def fingerprint():
 out={}
 for ds in CONFIG['datasets']:
  for kind in ['char','word']:
   I=Index.load(CACHE/(ds+'_'+kind+'.pkl'));h=hashlib.sha256()
   for a in [I.W.data,I.W.indices,I.W.indptr]:h.update(str(a.dtype).encode());h.update(a.tobytes())
   h.update(json.dumps(I.W.shape).encode());h.update(json.dumps(I.ids.tolist(),ensure_ascii=False).encode())
   h.update(json.dumps(sorted(I.v.vocabulary_.items()),ensure_ascii=False).encode())
   out[ds+'_'+kind]={'sha256':h.hexdigest(),'shape':list(I.W.shape),'nnz':int(I.W.nnz)}
   del I
 (RES/'index_fingerprints.json').write_text(json.dumps(out,indent=2))

if __name__=='__main__':
 if any(RES.glob('*_retention_confirmation.jsonl')):raise RuntimeError('Confirmation already exists; cannot call this a pre-test freeze')
 fingerprint();(ROOT/'config.json').write_text(json.dumps(CONFIG,indent=2))
 files=['core.py','rank_bound.py','screening.py','compatibility.py','enumeration.py','mip_reference.py','experiment.py','run.py','PROTOCOL.md','PROTOCOL_RETENTION.md','config.json','download_manifest.json','results/split_audit.json','results/index_fingerprints.json']
 files += ['results/'+ds+'_confirmation_ids.json' for ds in CONFIG['datasets']]
 freeze={'unix_time':time.time(),'python':sys.version,'platform':platform.platform(),'test_metrics_exist':False,
  'files':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files}}
 (RES/'confirmation_freeze.json').write_text(json.dumps(freeze,indent=2));print('Frozen',len(files),'files before confirmation')
