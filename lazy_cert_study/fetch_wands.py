"""Download pinned official inputs without overwriting local work."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    args=p.parse_args();args.data.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'sources.json').read_text())
    for item in manifest['files']:
        path=args.data/item['path'];path.parent.mkdir(parents=True,exist_ok=True)
        if not path.exists():
            temporary=path.with_name(path.name+'.part')
            with urllib.request.urlopen(item['url'],timeout=60) as src,temporary.open('xb') as dst:
                while True:
                    chunk=src.read(1024*1024)
                    if not chunk:break
                    dst.write(chunk)
            if hashlib.sha256(temporary.read_bytes()).hexdigest()!=item['sha256']:
                raise ValueError('Source hash mismatch: '+str(temporary))
            temporary.rename(path)
        assert path.stat().st_size==item['bytes']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']
        print('Verified',item['path'])
    destination=args.data/'source-manifest.json'
    if destination.exists():assert json.loads(destination.read_text())==manifest
    else:destination.write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
