from pathlib import Path
import json,hashlib,urllib.request
root=Path(__file__).resolve().parent
for i in json.loads((root/'fr_manifest.json').read_text()):
 p=root/'data/fr'/Path(i['path']).name.split('-')[0];p=p.with_suffix('.parquet');p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest()==i['sha256']:continue
 with urllib.request.urlopen(i['url'],timeout=240) as r:b=r.read()
 assert hashlib.sha256(b).hexdigest()==i['sha256']
 p.write_bytes(b);print('verified',p.name,len(b))
