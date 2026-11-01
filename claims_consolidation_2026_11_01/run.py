"""All-query replay of the EXISTING pipeline/refinement; no labels loaded."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='1'
import argparse,gzip,hashlib,json,platform,time,warnings
from pathlib import Path
import numpy as np
import scipy,sklearn
from threadpoolctl import threadpool_limits,threadpool_info
from reviewer_audit_2026_10_31.retention import load_inputs,context,kernel,normalize,native
from argon_followup_2026_11_01.refine import pairwise_refine

ROOT=Path(__file__).resolve().parent


def evaluate_context(C):
    if C['zero']:
        return C['n'],{'zeroWitness':True},{'rankUpper':C['n'],'status':'zero_witness','usesVerifiedLabels':False},0.
    baseline,detail=kernel(C['D'],C['Du'],C['lower'],'discrete',2)
    started=time.perf_counter()
    refinement=pairwise_refine(C['D'],C['Du'],baseline,budget=2,k=10,max_candidates=80,seconds=120.)
    extra=time.perf_counter()-started
    return baseline,detail,refinement,extra


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=False)
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    for name,sha in freeze['sourceHashes'].items():assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==sha,name
    meta={'status':'RUNNING','retrospective':True,'labelsReadByRunner':False,'python':platform.python_version(),
          'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'numericalThreads':1,
          'cpu':next(s.split(':',1)[1].strip() for s in Path('/proc/cpuinfo').read_text().splitlines() if s.startswith('model name')),
          'threadpools':threadpool_info(),'freezeSha256':hashlib.sha256((ROOT/'FREEZE.json').read_bytes()).hexdigest(),
          'timingScope':'Integrated prefix + incremental existing refinement; shared index load excluded','datasets':{}}
    (a.output/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    for ds,ids in freeze['queryIds'].items():
        index,texts,fp=load_inputs(a.data,ds);path=a.output/(ds+'.jsonl.gz')
        with gzip.open(path,'xt') as out:
            for number,qid in enumerate(ids,1):
                text=' '.join(normalize(texts[qid]).split()[:32]);started=time.perf_counter()
                C=context(index,text,2);after_context=time.perf_counter()
                baseline,detail,refinement,extra=evaluate_context(C);ended=time.perf_counter()
                total=ended-started;prefix=total-extra;rank=int(refinement['rankUpper'])
                assert 1<=rank<=baseline<=index.n
                row={'dataset':ds,'queryId':qid,'querySha256':hashlib.sha256(text.encode()).hexdigest(),
                     'modelFingerprint':fp,'referenceId':str(index.ids[C['ref']]),'corpusSize':index.n,
                     'candidateCount':None if C['zero'] else len(C['lower']),'baselineRankUpper':baseline,
                     'refinedRankUpper':rank,'baselineDetail':detail,'refinement':refinement,
                     'contextSeconds':after_context-started,'prefixSeconds':prefix,'extraSeconds':extra,'totalSeconds':total}
                out.write(json.dumps(native(row),separators=(',',':'))+'\n');out.flush()
                if number%10==0 or (rank<=10<baseline):
                    print(ds,number,'/',len(ids),qid,'rank',baseline,'->',rank,'route',refinement['status'],'total',round(total,3),flush=True)
        meta['datasets'][ds]={'queries':len(ids),'fingerprint':fp,'recordsSha256':hashlib.sha256(path.read_bytes()).hexdigest()}
        (a.output/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n');del index
    meta['status']='COMPLETE';meta['queries']=sum(len(v) for v in freeze['queryIds'].values())
    (a.output/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')


if __name__=='__main__':
    warnings.filterwarnings('ignore',message='.*Unrecognized options.*')
    with threadpool_limits(limits=1):main()
