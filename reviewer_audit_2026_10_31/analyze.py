"""Separate archived combined costs from newly controlled supplementary runs."""
from pathlib import Path
import argparse
import gzip
import hashlib
import json
import numpy as np
from scipy.stats import binomtest

ROOT=Path(__file__).resolve().parent


def load(path):
    with gzip.open(path,'rt') as f:return [json.loads(line) for line in f]


def holm(values):
    order=np.argsort(values);out=np.zeros(len(values));last=0.
    for rank,index in enumerate(order):
        last=max(last,min(1.,(len(values)-rank)*values[index]));out[index]=last
    return out.tolist()


def describe(values):
    return {key:float(value) for key,value in zip(['median','q25','q75','p95','total'],
        [np.median(values),np.quantile(values,.25),np.quantile(values,.75),np.quantile(values,.95),np.sum(values)])}


def analyze(run_dir):
    scope=json.loads((ROOT/'scope.json').read_text());datasets={};paired=[]
    for ds,ids in scope['replicationIds'].items():
        historical=load(ROOT.parent/'round3/results'/(ds+'_independent_replication.jsonl.gz'))
        assert [r['query_id'] for r in historical]==ids
        row={'queries':len(ids),'historicalCoverage':{
            method:sum(r[key]<=10 for r in historical)
            for method,key in [('pair_enum','pair_enum_rank_upper'),('best_lp_enum','best_lp_enum_rank_upper'),('discrete','proposed_rank_upper')]},
            'historicalCombinedSeconds':describe([r['seconds'] for r in historical]),
            'archivalTimingScope':'proposed+genericLP+diagnostics; concurrent jobs possible; NOT isolated per-method latency'}
        path=run_dir/(ds+'.jsonl.gz')
        if not path.exists() or not path.with_name(path.name+'.metadata.json').exists():
            row['supplementStatus']='BLOCKED_OR_NOT_RUN';row['milpCertified']=None
            row['controlledTiming']=None;datasets[ds]=row;continue
        metadata=json.loads(path.with_name(path.name+'.metadata.json').read_text())
        assert metadata['status']=='COMPLETE'
        assert metadata['outputSha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        records=load(path);assert [r['queryId'] for r in records]==ids
        methods=['best_lp_enum','discrete','milp_enum'];first={m:[] for m in methods}
        for record in records:
            for method in methods:
                selected=[r for r in record['runs'] if r['repeat']==0 and r['method']==method]
                assert len(selected)==1;first[method].append(selected[0])
        row['supplementStatus']='COMPLETE'
        row['supplementCoverage']={m:sum(r['rankUpper']<=10 for r in runs) for m,runs in first.items()}
        row['milpCertified']=row['supplementCoverage']['milp_enum']
        row['controlledTiming']={m:describe([r['seconds'] for r in runs]) for m,runs in first.items()}
        status={}
        for record in first['milp_enum']:
            d=record['detail'];solver=d.get('milp',{})
            key=('zero_reference' if d.get('zeroReference') else solver.get('skipped') or
                ('solver_status_'+str(solver.get('status'))))
            status[key]=status.get(key,0)+1
        row['milpStatusCounts']=status
        discrete=np.array([r['rankUpper']<=10 for r in first['discrete']])
        milp=np.array([r['rankUpper']<=10 for r in first['milp_enum']])
        diff=discrete.astype(int)-milp.astype(int);wins=int((diff>0).sum());losses=int((diff<0).sum())
        rng=np.random.default_rng(20261031+len(datasets))
        sample=diff[rng.integers(0,len(diff),size=(2000,len(diff)))].mean(axis=1)
        comparison={'dataset':ds,'wins':wins,'losses':losses,'difference':float(diff.mean()),
            'pairedBootstrap95':np.quantile(sample,[.025,.975]).tolist(),
            'twoSidedExactP':float(binomtest(wins,wins+losses,.5).pvalue) if wins+losses else 1.,
            'retrospective':True}
        paired.append(comparison)
        row['repeatedSubsetQueries']=len(scope['timingRepeatedSubset'][ds])
        row['repeatedSubsetNoise']={}
        for method in methods:
            ratios=[]
            for record in records:
                if record['queryId'] not in scope['timingRepeatedSubset'][ds]:continue
                t=[r['seconds'] for r in record['runs'] if r['method']==method]
                assert len(t)==3
                ratios.append(float(np.median(t)/t[0]))
            row['repeatedSubsetNoise'][method]=describe(ratios)
        datasets[ds]=row
    if len(paired)==3:
        for row,p in zip(paired,holm([r['twoSidedExactP'] for r in paired])):row['holmP']=p
    return {'status':'COMPLETE' if all(r['supplementStatus']=='COMPLETE' for r in datasets.values()) else 'INCOMPLETE',
        'retrospective':True,'datasets':datasets,'discreteVsMilp':paired,
        'interpretation':'Missing MILP values are unmeasured, not zero. Archived costs never stand in for controlled per-method timings.'}


def main():
    p=argparse.ArgumentParser();p.add_argument('--runs',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    report=analyze(args.runs)
    args.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':main()
