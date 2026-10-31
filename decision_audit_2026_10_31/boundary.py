"""All default-missed robust cases; explicit retrospective stress set."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import gzip,hashlib,json,time,argparse,warnings
from threadpoolctl import threadpool_limits
from reviewer_audit_2026_10_31.retention import load_inputs,context,normalize
from reviewer_audit_2026_10_31.verify_discordant import exhaustive_enclosure
from decision_audit_2026_10_31.budgets import PROFILES,profile_kernel

ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    freeze=json.loads((ROOT/'BOUNDARY_FREEZE.json').read_text());records=[]
    for path,digest in freeze['files'].items():assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==digest,path
    for ds,ids in freeze['queryIds'].items():
        if not ids:continue
        index,texts,model_hash=load_inputs(args.data,ds)
        for qid in ids:
            names=list(PROFILES)+['wide_enum'];shift=int(hashlib.sha256((ds+'|boundary|'+qid).encode()).hexdigest(),16)%len(names);order=names[shift:]+names[:shift];runs=[]
            text=' '.join(normalize(texts[qid]).split()[:32])
            for name in order:
                start=time.perf_counter();C=context(index,text,2);assert not C['zero']
                if name=='wide_enum':
                    detail=exhaustive_enclosure(C['Du']);rank=min(len(C['lower'])+1,detail.get('rankUpper',index.n))
                else:rank,detail=profile_kernel(C['D'],C['Du'],C['lower'],name)
                runs.append({'profile':name,'rankUpper':rank,'seconds':time.perf_counter()-start,'detail':detail})
            records.append({'dataset':ds,'queryId':qid,'verifiedLabel':'ROBUST','modelFingerprint':model_hash,'order':order,'runs':runs})
            print(ds,qid,{r['profile']:r['rankUpper'] for r in runs},flush=True)
        del index
    report={'status':'COMPLETE','retrospective':True,'outcomeSelectedCompleteBoundarySet':True,'queries':len(records),'rows':records,'scope':'All8 R minus(C_D intersection C_M); not independent confirmation or population timing'}
    args.output.write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':
    warnings.filterwarnings('ignore',message='.*Unrecognized options.*')
    with threadpool_limits(limits=1):main()
