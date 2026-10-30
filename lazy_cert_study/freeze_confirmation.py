"""Freeze prospective confirmation after development, without touching old data."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib
import json
import argparse
import subprocess

ROOT=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--development-analysis',type=Path,required=True)
    args=p.parse_args();destination=ROOT/'confirmation_freeze.json'
    if destination.exists():raise FileExistsError('A freeze may not be silently replaced')
    dev=json.loads(args.development_analysis.read_text())
    assert dev['queries']==64 and dev['candidate']=='screen_batch'
    files=list(ROOT.glob('*.py'))+[ROOT/x for x in ['PROTOCOL.md','THEORY.md','sources.json','selection.json']]
    files+=[ROOT.parent/'pool_study/core.py',ROOT.parent/'exact_pool_study/method.py']
    manifest={'frozenUTC':datetime.now(timezone.utc).isoformat(),
        'baseGitCommit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT.parent,text=True).strip(),
        'candidate':'screen_batch','developmentQueries':64,'confirmationQueries':128,
        'reservedUnseen':288,'developmentAnalysisSha256':hashlib.sha256(args.development_analysis.read_bytes()).hexdigest(),
        'primaryTests':['certificateVsFastestControl','distinct20VsFastestOnlineControl'],
        'note':'Engineering confirmation only. Not an originality or Q1 adjudication.',
        'files':{str(f.relative_to(ROOT.parent)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(files)}}
    destination.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))


if __name__=='__main__':main()
