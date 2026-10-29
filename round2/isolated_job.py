"""Run unchanged final protocol for one dataset in an isolated output directory."""
import os,sys
from pathlib import Path
import run
name=sys.argv[1];original=run.RES;out=run.ROOT/'jobs'/name;out.mkdir(parents=True,exist_ok=True)
for n in [name+'_prepared.pkl','selected.json','selection_freeze.json']:
 p=out/n
 if not p.exists():p.symlink_to(original/n)
run.RES=out;run.DS=[name];run.final()
