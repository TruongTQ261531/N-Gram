"""Replay all266 robust graphs; strengthen all seven default-missed cases."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,gzip,hashlib,itertools,json,time
from pathlib import Path
from reviewer_audit_2026_10_31.retention import load_inputs,context,normalize,native,cover_bound
from compatibility import incompatible
from argon_followup_2026_11_01.graph import complement,greedy,maximum_clique,coloring

ROOT=Path(__file__).resolve().parent


def solve_graph(n,checks,original_groups=None):
    edges=[(r['left'],r['right']) for r in checks if r['incompatible']]
    adj=complement(n,edges);ds=greedy(adj)
    initial=original_groups if original_groups is not None and len(original_groups)<len(ds) else ds
    w=maximum_clique(adj,5.);c=coloring(adj,w['size'],5.,initial)
    return {'conflictEdges':edges,'dsaturGreedyColors':len(ds),'maxClique':w,'coloring':c,
            'pairwiseUpper':w['size'] if w['optimal'] else c['colors']}


def main():
    p=argparse.ArgumentParser();p.add_argument('--data',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    with gzip.open(ROOT.parent/'decision_audit_2026_10_31/results/decisions.json.gz','rt') as f:
        selected=[r for r in json.load(f)['rows'] if r['label']=='ROBUST']
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(a.output,'xt') as out:
        for ds in ['scifact','nfcorpus','fiqa']:
            cases=[r for r in selected if r['dataset']==ds];index,texts,fp=load_inputs(a.data,ds)
            for number,old in enumerate(cases,1):
                started=time.perf_counter();qid=old['queryId'];C=context(index,' '.join(normalize(texts[qid]).split()[:32]),2)
                assert not C['zero'];n=len(C['lower']);original=cover_bound(C['D'],C['Du'],2,120,80)
                row={'dataset':ds,'queryId':qid,'modelFingerprint':fp,'candidateCount':n,'originalBounds':old['originalBounds'],
                     'greedy':native(original),'contextAndOriginalGraphSeconds':time.perf_counter()-started}
                if n<=80:
                    row['sameGraph']=solve_graph(n,original['checks'],original['groups'])
                    row['sameGraphRankUpper']=min(old['originalBounds']['discrete'],row['sameGraph']['pairwiseUpper']+1)
                else:row['sameGraphSkipped']='candidate_cap';row['sameGraphRankUpper']=old['originalBounds']['discrete']
                if old['originalBounds']['discrete']>10:
                    start=time.perf_counter();checks=[];complete=True
                    for i,j in itertools.combinations(range(n),2):
                        if time.perf_counter()-start>120:complete=False;break
                        r=incompatible([d[:,[i,j]] for d in C['D']],[u[:,[i,j]] for u in C['Du']],2)
                        checks.append(native({**r,'left':i,'right':j}))
                    row['fullPairConstructionSeconds']=time.perf_counter()-start
                    row['allPairsChecked']=complete;row['fullChecks']=checks
                    row['fullGraph']=solve_graph(n,checks)
                    row['fullGraphRankUpper']=min(old['originalBounds']['discrete'],row['fullGraph']['pairwiseUpper']+1)
                out.write(json.dumps(native(row),separators=(',',':'))+'\n');out.flush()
                if number%10==0 or old['originalBounds']['discrete']>10:
                    print(ds,number,'/',len(cases),qid,'n',n,'rank',row['sameGraphRankUpper'],row.get('fullGraphRankUpper'),flush=True)
            del index


if __name__=='__main__':main()
