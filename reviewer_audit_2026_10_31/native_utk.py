"""Run a private native UTK build on an exact continuous-domain fixture.

No third-party source, executable, or downloaded paper is redistributed.
This is conformance/domain evidence, not a matched NLP timing comparison.
The private main.cpp harness must honor -q and export one AUDIT_IDS line.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
from reviewer_audit_2026_10_31.contract_checks import region_fixture

UPSTREAM='https://github.com/cupermanrose/UTK_source'
COMMIT='16466c87b08e2e368ba870cdcbbf31dc36be406b'
POINTS='1 1 0 0 1 0 0\n2 0 1 1 0 1 1\n3 0.625 0.625 0.625 0.625 0.625 0.625\n'
REGION='0.25 0.75 0.05 0.10\n'


def parse_ids(log):
    lines=re.findall(r'^AUDIT_IDS(.*)$',log,re.MULTILINE)
    if len(lines)!=1:raise ValueError('Expected exactly one AUDIT_IDS result')
    return sorted({int(x) for x in lines[0].split()})


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--binary',type=Path,required=True)
    p.add_argument('--source',type=Path,required=True)
    p.add_argument('--qhull-bin',type=Path,required=True)
    p.add_argument('--variant',choices=['io-only','guard-corrected'],required=True)
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    binary=args.binary.resolve();source=args.source.resolve();out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=False)
    (out/'points.txt').write_text(POINTS);(out/'region.txt').write_text(REGION)
    report={'scope':'Native continuous-region conformance, NOT matched NLP baseline/runtime',
        'upstream':UPSTREAM,'upstreamCommit':COMMIT,'localVariant':args.variant,
        'binarySha256':hashlib.sha256(binary.read_bytes()).hexdigest(),
        'localSourceHashes':{name:hashlib.sha256((source/name).read_bytes()).hexdigest()
            for name in ['src/main.cpp','src/utk.cpp','src/cellTree.cpp','src/skyline.cpp']},
        'fixture':region_fixture(),'runs':{},'thirdPartyFilesRedistributed':False}
    env=os.environ.copy();env['PATH']=str(args.qhull_bin.resolve())+os.pathsep+env['PATH']
    for method in ['RSA','JAA']:
        cwd=out/method;cwd.mkdir()
        cmd=[str(binary),'-d','3','-k','1','-f',str(out/'points.txt'),
             '-i','index.bin','-q',str(out/'region.txt'),'-R','0.1','-m',method]
        try:
            run=subprocess.run(cmd,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,timeout=45,check=False)
            log=run.stdout;ids=parse_ids(log) if run.returncode==0 else None
            row={'exitCode':run.returncode,'reportedIds':ids,
                'matchesContinuousUnion':ids==report['fixture']['continuousUnion']}
        except subprocess.TimeoutExpired as e:
            log=e.stdout or b''
            if isinstance(log,bytes):log=log.decode(errors='replace')
            row={'status':'TIMEOUT','matchesContinuousUnion':False}
        (out/(method+'.stdout.txt')).write_text(log)
        row['logSha256']=hashlib.sha256(log.encode()).hexdigest();report['runs'][method]=row
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['runs'],indent=2))


if __name__=='__main__':main()
