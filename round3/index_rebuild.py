"""Rebuild SciFact indexes from pinned raw data, without using cache pickles."""
from core import Index,normalize
from run import sources
from pathlib import Path
import json,hashlib,time
R=Path(__file__).resolve().parent
def main():
 c,_=sources('scifact');texts=(c['title']+' '+c['text']).map(normalize).tolist();expected=json.loads((R/'results/index_fingerprints.json').read_text());rows=[]
 for kind in ['char','word']:
  t=time.perf_counter();I=Index(texts,c['_id'].tolist(),kind);h=hashlib.sha256()
  for a in [I.W.data,I.W.indices,I.W.indptr]:h.update(str(a.dtype).encode());h.update(a.tobytes())
  h.update(json.dumps(I.W.shape).encode());h.update(json.dumps(I.ids.tolist(),ensure_ascii=False).encode());h.update(json.dumps(sorted(I.v.vocabulary_.items()),ensure_ascii=False).encode());actual=h.hexdigest();assert actual==expected['scifact_'+kind]['sha256']
  rows.append({'dataset':'scifact','kind':kind,'sha256':actual,'matched':True,'seconds':time.perf_counter()-t});print(kind,'independently rebuilt index matched frozen canonical fingerprint',flush=True);del I
 (R/'results/index_rebuild.json').write_text(json.dumps(rows,indent=2))
if __name__=='__main__':main()
