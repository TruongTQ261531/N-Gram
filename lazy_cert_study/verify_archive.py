"""Audit completed run integrity, paired outputs and exact pool contracts."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parent
METHODS={'memo','incremental','batch','parent','screened','screen_batch'}


def verify(path,phase):
    metadata=json.loads(path.with_name(path.name+'.metadata.json').read_text())
    assert metadata.get('finishedUTC'),'Interrupted run'
    assert metadata['outputSha256']==hashlib.sha256(path.read_bytes()).hexdigest()
    with gzip.open(path,'rt') as f:rows=[json.loads(s) for s in f]
    selected=json.loads((ROOT/'selection.json').read_text())[phase]
    assert [r['queryId'] for r in rows]==selected,'Missing/reordered/extra queries'
    repeats=metadata['repeats'];checks=0
    for row in rows:
        assert row['modelHash']==metadata['modelHash']
        for scenario,measurements in row['scenarios'].items():
            assert len(measurements)==len(METHODS)*repeats
            assert len({m['answerSha256'] for m in measurements})==1
            assert {(m['method'],m['repeat']) for m in measurements}=={
                (method,r) for method in METHODS for r in range(repeats)}
            for m in measurements:
                t=m['prefixSeconds'];assert 0<t['1']<=t['5']<=t['20']<=m['seconds']
                if m['build']:
                    d=m['build'];pool=d['pool'];assert pool==sorted(set(pool))
                    assert d['status'] in ('exact','resource_unknown')
                    if row['oracleUnion'] is not None:
                        if d['status']=='exact':assert pool==row['oracleUnion']
                        else:assert set(row['oracleUnion'])<=set(pool)
                checks+=1
    if phase=='confirmation':
        freeze=json.loads((ROOT/'confirmation_freeze.json').read_text())
        for file,digest in freeze['files'].items():
            assert hashlib.sha256((ROOT.parent/file).read_bytes()).hexdigest()==digest,file
        assert metadata['startedUTC']>freeze['frozenUTC']
        assert repeats==3
    return {'queries':len(rows),'validatedSessions':checks,
            'oracleExact':sum(r['oracle']['status']=='exact' for r in rows),
            'sha256':metadata['outputSha256'],'status':'PASS'}


def main():
    p=argparse.ArgumentParser();p.add_argument('input',type=Path)
    p.add_argument('--phase',choices=['development','confirmation'],required=True)
    args=p.parse_args();print(json.dumps(verify(args.input,args.phase),indent=2))


if __name__=='__main__':main()
