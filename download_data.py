"""Download byte-identical pinned public mirrors; no Hugging Face token needed."""
from pathlib import Path
import json,hashlib,urllib.request
root=Path(__file__).resolve().parent
for item in json.loads((root/'download_manifest.json').read_text()):
 p=root/'data'/item['repo'].split('/')[-1]/item['file'];p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']:continue
 with urllib.request.urlopen(item['url'],timeout=120) as r:data=r.read()
 assert hashlib.sha256(data).hexdigest()==item['sha256'],item['file']
 p.write_bytes(data);print('verified',p.name,len(data))
