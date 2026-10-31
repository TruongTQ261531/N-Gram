"""Restore exact historical input bytes; never substitute another corpus."""
from pathlib import Path
import argparse
import hashlib
import json
import urllib.request

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--fetch',action='store_true');p.add_argument('--report',type=Path,required=True)
    args=p.parse_args();args.data.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT.parent/'round3/download_manifest.json').read_text())
    rows=[];network_failed=False
    for item in manifest:
        relative=Path(item['local'])
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe manifest path')
        path=args.data/relative
        row={'path':str(relative),'expectedSha256':item['sha256']}
        if not path.exists() and args.fetch and not network_failed:
            path.parent.mkdir(parents=True,exist_ok=True)
            temporary=path.with_name(path.name+'.part')
            try:
                with urllib.request.urlopen(item['url'],timeout=60) as src,temporary.open('xb') as dst:
                    while True:
                        chunk=src.read(1024*1024)
                        if not chunk:break
                        dst.write(chunk)
                assert hashlib.sha256(temporary.read_bytes()).hexdigest()==item['sha256']
                temporary.rename(path)
            except Exception as error:
                network_failed=True;row['downloadError']=str(error)
        row['status']='missing'
        if path.exists():
            if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:
                raise ValueError('Preserving mismatched local file: '+str(path))
            row['status']='verified'
        rows.append(row)
    report={'status':'READY' if all(r['status']=='verified' for r in rows) else 'BLOCKED',
        'files':rows,'verified':sum(r['status']=='verified' for r in rows),'required':len(rows),
        'reason':'Exact historical source bytes required; no synthetic/replacement data permitted.'}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='files'},indent=2))
    if report['status']!='READY':raise SystemExit(2)


if __name__=='__main__':main()
