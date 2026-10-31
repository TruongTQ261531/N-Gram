"""Paired wider enumeration versus unchanged Discrete; all outcomes retained."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
from pathlib import Path
import argparse,gzip,hashlib,json,time,warnings
from threadpoolctl import threadpool_limits,threadpool_info
from reviewer_audit_2026_10_31.retention import load_inputs,context,normalize,kernel
from reviewer_audit_2026_10_31.verify_discordant import exhaustive_enclosure

ROOT=Path(__file__).resolve().parent

def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True)
    p.add_argument('--dataset',choices=['scifact','nfcorpus','fiqa'],required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    freeze=json.loads((ROOT/'WIDE_ENUM_FREEZE.json').read_text())
    for name,digest in freeze['files'].items():assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==digest,name
    index,texts,model_hash=load_inputs(args.data,args.dataset);ids=freeze['timingPanelIds'][args.dataset]
    with gzip.open(ROOT.parent/'reviewer_audit_2026_10_31/results/retention'/(args.dataset+'.jsonl.gz'),'rt') as f:
        prior={r['queryId']:r for r in map(json.loads,f)}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(args.output,'xt') as out:
        for number,qid in enumerate(ids,1):
            text=' '.join(normalize(texts[qid]).split()[:32]);order=['wide_enum','discrete_default']
            if int(hashlib.sha256((args.dataset+'|wide|'+qid).encode()).hexdigest(),16)%2:order.reverse()
            runs=[]
            for method in order:
                start=time.perf_counter();C=context(index,text,2)
                if C['zero']:rank=index.n;detail={'zeroReference':True}
                elif method=='wide_enum':
                    detail=exhaustive_enclosure(C['Du']);rank=min(len(C['lower'])+1,detail.get('rankUpper',index.n))
                else:rank,detail=kernel(C['D'],C['Du'],C['lower'],'discrete')
                seconds=time.perf_counter()-start
                if method=='discrete_default':assert rank==prior[qid]['oldDiscreteRank']
                runs.append({'method':method,'rankUpper':rank,'seconds':seconds,'detail':detail})
            out.write(json.dumps({'dataset':args.dataset,'queryId':qid,'order':order,'runs':runs},separators=(',',':'))+'\n');out.flush()
            print(args.dataset,number,'/',len(ids),qid,round(sum(r['seconds'] for r in runs),3),flush=True)
    metadata={'status':'COMPLETE','retrospective':True,'queries':48,'modelFingerprint':model_hash,
        'rowsSha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'freezeSha256':hashlib.sha256((ROOT/'WIDE_ENUM_FREEZE.json').read_bytes()).hexdigest(),
        'threadpools':threadpool_info(),'scope':'Separate paired block,2million states/500million cells; no new confirmation'}
    args.output.with_name(args.output.name+'.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')

if __name__=='__main__':
    warnings.filterwarnings('ignore',message='.*Unrecognized options.*')
    with threadpool_limits(limits=1):main()
