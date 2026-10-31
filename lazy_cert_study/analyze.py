"""Query-paired analysis; timing repetitions are never independent samples."""
from pathlib import Path
import argparse
import gzip
import json
import numpy as np
from scipy.stats import binomtest

METHODS=['memo','incremental','batch','parent','screened','screen_batch']


def paired(candidate,control):
    log=np.log(np.asarray(control)/np.asarray(candidate))
    rng=np.random.default_rng(20261031)
    means=log[rng.integers(0,len(log),size=(20000,len(log)))].mean(axis=1)
    wins=int((log>0).sum());ties=int((log==0).sum())
    return {'n':len(log),'wins':wins,'ties':ties,
        'geometricSpeedup':float(np.exp(log.mean())),
        'pairedBootstrap95':np.exp(np.quantile(means,[.025,.975])).tolist(),
        'oneSidedSignP':float(binomtest(wins,len(log)-ties,.5,alternative='greater').pvalue)
            if len(log)>ties else 1.}


def analyze(path,candidate='screen_batch'):
    with gzip.open(path,'rt') as f:rows=[json.loads(line) for line in f]
    assert len({r['queryId'] for r in rows})==len(rows)
    report={'queries':len(rows),'candidate':candidate,
        'oracleExact':sum(r['oracle']['status']=='exact' for r in rows),'scenarios':{}}
    builds={m:[] for m in METHODS[2:]}
    for r in rows:
        for m in builds:
            builds[m].append(float(np.median([x['build']['seconds']
                for seq in r['scenarios'].values() for x in seq if x['method']==m])))
    report['certificateMedianMs']={m:1000*float(np.median(v)) for m,v in builds.items()}
    report['certificateVsFastestControl']=paired(builds[candidate],np.minimum(builds['batch'],builds['parent']))
    report['exactResults']={m:sum(all(x['build']['status']=='exact'
        for seq in r['scenarios'].values() for x in seq if x['method']==m) for r in rows) for m in builds}
    report['medianPool']=float(np.median([len(next(x['build']['pool'] for x in r['scenarios']['distinct']
        if x['method']==candidate)) for r in rows]))
    report['medianInitialPool']=float(np.median([next(x['build']['initialPool']
        for x in r['scenarios']['distinct'] if x['method']==candidate) for r in rows]))
    report['fullCorpusTies']=sum(len(next(x['build']['pool'] for x in r['scenarios']['distinct']
        if x['method']==candidate))==42994 for r in rows)
    for scenario in ['distinct','repeated']:
        entry={}
        for prefix in ['1','5','20']:
            times={m:[float(np.median([x['prefixSeconds'][prefix]
                for x in r['scenarios'][scenario] if x['method']==m])) for r in rows] for m in METHODS}
            entry[prefix]={'medianMs':{m:1000*float(np.median(t)) for m,t in times.items()},
                'vsFastestOnlineControl':paired(times[candidate],np.minimum(times['memo'],times['incremental']))}
        report['scenarios'][scenario]=entry
    primary=[report['certificateVsFastestControl'],
        report['scenarios']['distinct']['20']['vsFastestOnlineControl']]
    ordered=sorted(range(2),key=lambda j:primary[j]['oneSidedSignP']);last=0.
    for rank,j in enumerate(ordered):
        last=max(last,min(1.,(2-rank)*primary[j]['oneSidedSignP']))
        primary[j]['holmP']=last
    report['gates']={
        'correctness':report['oracleExact']==len(rows) and report['exactResults'][candidate]==len(rows),
        'certificateUseful':primary[0]['geometricSpeedup']>=1.2 and primary[0]['pairedBootstrap95'][0]>1 and primary[0]['holmP']<.05,
        'onlineUseful':primary[1]['geometricSpeedup']>=1.2 and primary[1]['pairedBootstrap95'][0]>1 and primary[1]['holmP']<.05,
        'q1OrNoveltyEstablished':False}
    return report


def main():
    p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--candidate',choices=METHODS[2:],default='screen_batch');args=p.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    report=analyze(args.input,args.candidate)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
