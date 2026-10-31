"""Retrospective independent budget profiles; not a continuous anytime trace."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import argparse,gzip,hashlib,json,time,warnings
import numpy as np
from threadpoolctl import threadpool_limits,threadpool_info
from reviewer_audit_2026_10_31.retention import load_inputs,context,normalize,native,envelope,cover_bound,exhaustive_count,mip_solve,kernel

ROOT=Path(__file__).resolve().parent
PROFILES={
    'discrete_fast':{'kind':'discrete','cuts':10,'pairs':30},
    'milp_0p1':{'kind':'milp','solverSeconds':.1},
    'discrete_default':{'kind':'discrete','cuts':40,'pairs':120},
    'milp_1':{'kind':'milp','solverSeconds':1.},
    'discrete_extended':{'kind':'discrete','cuts':160,'pairs':480},
    'milp_5':{'kind':'milp','solverSeconds':5.}}

def profile_kernel(D,Du,lower,name):
    profile=PROFILES[name];m=len(lower);enum=exhaustive_count(D,Du,2)
    rank=min(m+1,int(enum.get('rank_upper',m+1)))
    detail={'pairRank':m+1,'enumRank':enum.get('rank_upper'),'enumStatus':enum.get('skipped','complete')}
    if profile['kind']=='discrete':
        lp=envelope(D,Du,lower,2,profile['cuts'])
        graph=cover_bound(D,Du,2,profile['pairs'],80)
        rank=min(rank,int(np.floor(np.nextafter(lp['upper_count'],np.inf)))+1,graph['count_upper']+1)
        detail.update({'cutsUsed':lp['iterations'],'graphRank':graph['count_upper']+1,'graphSkipped':graph.get('skipped')})
    else:
        milp=mip_solve(Du,lower,2,profile['solverSeconds']);detail['milp']=milp
        if milp.get('count_upper') is not None:
            rank=min(rank,int(np.floor(np.nextafter(milp['count_upper']+1e-6,np.inf)))+1)
    return rank,native(detail)

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--dataset',choices=['scifact','nfcorpus','fiqa'],required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    freeze=json.loads((ROOT/'BUDGET_FREEZE.json').read_text())
    for file,digest in freeze['files'].items():assert hashlib.sha256((ROOT.parent/file).read_bytes()).hexdigest()==digest,file
    ids=freeze['timingPanelIds'][args.dataset];index,texts,model_hash=load_inputs(args.data,args.dataset)
    path=ROOT.parent/'reviewer_audit_2026_10_31/results/retention'/(args.dataset+'.jsonl.gz')
    with gzip.open(path,'rt') as f:prior={r['queryId']:r for r in map(json.loads,f)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(args.output,'xt') as out:
        for number,qid in enumerate(ids,1):
            text=' '.join(normalize(texts[qid]).split()[:32]);names=list(PROFILES)
            shift=int(hashlib.sha256((args.dataset+'|budget|'+qid).encode()).hexdigest(),16)%len(names)
            order=names[shift:]+names[:shift];runs=[]
            for name in order:
                start=time.perf_counter();C=context(index,text,2)
                if C['zero']:rank=index.n;detail={'zeroReference':True}
                else:rank,detail=profile_kernel(C['D'],C['Du'],C['lower'],name)
                seconds=time.perf_counter()-start
                if name=='discrete_default':assert rank==prior[qid]['oldDiscreteRank'],(args.dataset,qid,rank)
                runs.append({'profile':name,'seconds':seconds,'rankUpper':rank,'detail':detail})
            out.write(json.dumps({'dataset':args.dataset,'queryId':qid,'order':order,'runs':runs},separators=(',',':'))+'\n');out.flush()
            print(args.dataset,number,'/',len(ids),qid,'seconds',round(sum(r['seconds'] for r in runs),3),flush=True)
    metadata={'status':'COMPLETE','retrospective':True,'queries':len(ids),'profiles':PROFILES,
        'interpretation':'Independent budget-setting runs, not a continuous anytime trace; no monotone best-of selection',
        'modelFingerprint':model_hash,'numericalThreads':1,'threadpools':threadpool_info(),
        'rowsSha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'freezeSha256':hashlib.sha256((ROOT/'BUDGET_FREEZE.json').read_bytes()).hexdigest()}
    args.output.with_name(args.output.name+'.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')

if __name__=='__main__':
    warnings.filterwarnings('ignore',message='.*Unrecognized options.*')
    with threadpool_limits(limits=1):main()
