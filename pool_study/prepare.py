"""Download pinned public inputs; select query IDs without looking at scores."""
from pathlib import Path
import argparse,hashlib,json,urllib.request
import pandas as pd

ROOT = Path(__file__).resolve().parent
PINNED = {'arguana':'9bcf8fc0320c4e3860e25b8b85fa205fcdd7078f','scidocs':'acebceec772628c6679d76d6cff30ad517d17f4e'}

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);a=p.parse_args()
    manifest=[];selection={}
    for ds,revision in PINNED.items():
        base=a.data/ds;base.mkdir(parents=True,exist_ok=True)
        for name in ['README.md','corpus/corpus-00000-of-00001.parquet','queries/queries-00000-of-00001.parquet']:
            target=base/name;target.parent.mkdir(parents=True,exist_ok=True)
            url=f'https://huggingface.co/datasets/BeIR/{ds}/resolve/{revision}/{name}'
            if not target.exists():
                with urllib.request.urlopen(url,timeout=120) as f:target.write_bytes(f.read())
            manifest.append({'dataset':ds,'revision':revision,'path':name,'url':url,'bytes':target.stat().st_size,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'license':'CC-BY-SA-4.0 per pinned HF card; see DATA_LICENSE.md'})
        q=pd.read_parquet(base/'queries/queries-00000-of-00001.parquet')
        corpus=pd.read_parquet(base/'corpus/corpus-00000-of-00001.parquet')
        ids=sorted(q['_id'].astype(str),key=lambda x:hashlib.sha256(('pool-v1|'+ds+'|'+x).encode()).digest())[:64]
        selection[ds]={'queryIds':ids,'queriesAvailable':len(q),'corpusDocuments':len(corpus),'selection':'first64 by SHA256(pool-v1|dataset|queryId), before any scores'}
        print(ds,'documents',len(corpus),'queries',len(q),'selected',len(ids),flush=True)
    (ROOT/'sources.json').write_text(json.dumps(manifest,indent=2))
    (ROOT/'selection.json').write_text(json.dumps(selection,indent=2))

if __name__=='__main__':main()
