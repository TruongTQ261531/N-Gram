"""Post-run labels join; never imported by the replay/routing runner."""
import gzip,hashlib,itertools,json,math
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parent


def distribution(values):
    if not values:return None
    x=np.asarray(values,dtype=float)
    return {'n':len(x),'median':float(np.median(x)),'p95':float(np.quantile(x,.95)),
            'max':float(x.max()),'sum':float(x.sum())}


def analyze():
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    for name,sha in freeze['sourceHashes'].items():
        assert hashlib.sha256((ROOT.parent/name).read_bytes()).hexdigest()==sha,name
    meta=json.loads((ROOT/'results/metadata.json').read_text())
    assert meta['status']=='COMPLETE' and meta['queries']==970
    assert meta['labelsReadByRunner'] is False and meta['numericalThreads']==1
    assert meta['freezeSha256']==hashlib.sha256((ROOT/'FREEZE.json').read_bytes()).hexdigest()
    labels_path=ROOT.parent/'decision_audit_2026_10_31/results/decisions.json.gz'
    with gzip.open(labels_path,'rt') as f:labels=json.load(f)['rows']
    labels={(r['dataset'],r['queryId']):r for r in labels}
    allrows=[]
    for ds,ids in freeze['queryIds'].items():
        path=ROOT/'results'/(ds+'.jsonl.gz')
        assert meta['datasets'][ds]['recordsSha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        with gzip.open(path,'rt') as f:rows=[json.loads(line) for line in f]
        assert [r['queryId'] for r in rows]==ids
        assert all(r['dataset']==ds for r in rows)
        allrows.extend(rows)
    assert len(allrows)==len(labels)==970
    assert {(r['dataset'],r['queryId']) for r in allrows}==set(labels)
    for r in allrows:
        truth=labels[(r['dataset'],r['queryId'])];ref=r['refinement'];n=r['candidateCount']
        assert r['modelFingerprint']==truth['modelFingerprint']
        assert r['referenceId']==truth['referenceId']
        assert 1<=r['refinedRankUpper']<=r['baselineRankUpper']<=r['corpusSize']
        assert r['refinedRankUpper']==ref['rankUpper']
        assert all(math.isfinite(r[k]) and r[k]>=0 for k in ['contextSeconds','prefixSeconds','extraSeconds','totalSeconds'])
        assert r['contextSeconds']<=r['prefixSeconds']
        assert abs(r['prefixSeconds']+r['extraSeconds']-r['totalSeconds'])<1e-9
        if ref['status']=='zero_witness':
            assert n is None and r['refinedRankUpper']==r['corpusSize']
        elif ref['status']=='already_certified':assert r['baselineRankUpper']<=10
        elif ref['status']=='candidate_cap':assert n>80 and r['baselineRankUpper']>10
        else:
            assert ref['status'] in ['complete_pairs','construction_cap']
            assert r['baselineRankUpper']>10 and n<=80 and ref['usesVerifiedLabels'] is False
            checks=ref['checks'];groups=ref['groups']
            pairs=[(c['left'],c['right']) for c in checks]
            assert len(pairs)==len(set(pairs)) and all(0<=i<j<n for i,j in pairs)
            assert pairs==list(itertools.combinations(range(n),2))[:len(pairs)]
            if ref['status']=='complete_pairs':assert len(pairs)==n*(n-1)//2
            edges={(c['left'],c['right']) for c in checks if c['incompatible']}
            assert all(not c['incompatible'] or c['upper']<0 for c in checks)
            assert sorted(i for g in groups for i in g)==list(range(n))
            assert all(tuple(sorted((i,j))) in edges for g in groups for i,j in itertools.combinations(g,2))
            assert r['refinedRankUpper']==min(r['baselineRankUpper'],len(groups)+1)

    def summarize(rows):
        robust=[r for r in rows if labels[(r['dataset'],r['queryId'])]['label']=='ROBUST']
        nonrobust=[r for r in rows if labels[(r['dataset'],r['queryId'])]['label']=='NONROBUST']
        routed=[r for r in rows if r['refinement']['status'] in ['complete_pairs','construction_cap']]
        improved=[r for r in rows if r['refinedRankUpper']<r['baselineRankUpper']]
        new=[r for r in rows if r['refinedRankUpper']<=10<r['baselineRankUpper']]
        differences=[{'queryId':r['queryId'],'old':labels[(r['dataset'],r['queryId'])]['originalBounds']['discrete'],
                      'replayed':r['baselineRankUpper']} for r in rows
                     if r['baselineRankUpper']!=labels[(r['dataset'],r['queryId'])]['originalBounds']['discrete']]
        return {'queries':len(rows),'robust':len(robust),'nonrobust':len(nonrobust),
                'baselineCertified':sum(r['baselineRankUpper']<=10 for r in rows),
                'refinedCertified':sum(r['refinedRankUpper']<=10 for r in rows),
                'falseCertifications':[r['queryId'] for r in nonrobust if r['refinedRankUpper']<=10],
                'routes':dict(sorted(Counter(r['refinement']['status'] for r in rows).items())),
                'routedNonrobust':sum(labels[(r['dataset'],r['queryId'])]['label']=='NONROBUST' for r in routed),
                'improvedBounds':len(improved),'newCertificates':[r['queryId'] for r in new],
                'baselineBoundDifferences':differences,
                'timing':{panel:{k:distribution([r[k] for r in selected]) for k in ['prefixSeconds','extraSeconds','totalSeconds']}
                          for panel,selected in [('all',rows),('routed',routed),('robust',robust),('nonrobust',nonrobust)]},
                'pairChecks':sum(len(r['refinement'].get('checks',[])) for r in rows),
                'pairProofMethods':dict(sorted(Counter(c['method'] for r in rows for c in r['refinement'].get('checks',[])).items())),
                'pairResourceCaps':sum(c['method']=='resource_cap' for r in rows for c in r['refinement'].get('checks',[])),
                'unprovedPairMethods':dict(sorted(Counter(c['method'] for r in rows for c in r['refinement'].get('checks',[]) if not c['incompatible']).items())),
                'defaultEnumerationStatuses':dict(sorted(Counter(r['baselineDetail'].get('enumStatus','zero_witness') for r in rows).items())),
                'defaultGraphSkipped':dict(sorted(Counter(str(r['baselineDetail'].get('graphSkipped','zero_witness')) for r in rows).items()))}
    return {'status':'COMPLETE','retrospective':True,'labelsReadByRunner':False,
            'decisionArchiveSha256':hashlib.sha256(labels_path.read_bytes()).hexdigest(),
            'timingScope':meta['timingScope'],'total':summarize(allrows),
            'datasets':{ds:summarize([r for r in allrows if r['dataset']==ds]) for ds in freeze['queryIds']}}


if __name__=='__main__':
    result=analyze();assert not result['total']['falseCertifications']
    (ROOT/'results/analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result['total'].items() if k!='timing'},indent=2))
