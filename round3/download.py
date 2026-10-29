"""Pinned BEIR sources. Corpus/qrels are local only, never part of publication."""
from pathlib import Path
import hashlib,json,urllib.request

ROOT=Path(__file__).resolve().parent
PINS={
 'scifact':('b3b5335604bf5ee3c4447671af975ea25143d4f5','2938d17dc3b09882fdb8c12bbbe2e2dc0e75a029'),
 'nfcorpus':('b5026a0e96e8a7ac4f95f482a596389289d46269','a451b3b26d3ae1358f259c1a3a4dd61fcea35a65'),
 'fiqa':('979c07a7cb5ccc6ca009792241fa1250b98055dd','252958f2d646e22cab6d0c72dd3f0d5de6d0655a')}

def fetch(url):
 with urllib.request.urlopen(url,timeout=240) as r:return r.read()

def main():
 manifest=[]
 for name,revs in PINS.items():
  for qrel,rev in enumerate(revs):
   repo='BeIR/'+name+('-qrels' if qrel else '')
   d=json.loads(fetch('https://huggingface.co/api/datasets/'+repo+'/revision/'+rev+'?blobs=true'))
   assert d['sha']==rev
   for f in d['siblings']:
    path=f['rfilename']
    if not (path.endswith(('.parquet','.tsv')) or path=='README.md'):continue
    local=ROOT/'data'/name/('qrels' if qrel else 'source')/path
    local.parent.mkdir(parents=True,exist_ok=True)
    url='https://huggingface.co/datasets/'+repo+'/resolve/'+rev+'/'+path
    b=local.read_bytes() if local.exists() else fetch(url)
    if 'lfs' in f:assert hashlib.sha256(b).hexdigest()==f['lfs']['sha256']
    else:assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==f['blobId']
    local.write_bytes(b)
    manifest.append({'repo':repo,'revision':rev,'path':path,'local':str(local.relative_to(ROOT)),
      'url':url,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b),'card_license':d.get('cardData',{}).get('license')})
    print('verified',name,str(local.relative_to(ROOT)),len(b),flush=True)
 (ROOT/'download_manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
