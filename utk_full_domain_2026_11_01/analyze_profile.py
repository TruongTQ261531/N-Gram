"""Check the separately frozen wall-only profile, linking identical factors."""
import gzip,json,hashlib
from collections import Counter
import numpy as np
from utk_full_domain_2026_11_01.run import ROOT,METHODS,digest
from utk_full_domain_2026_11_01.archive import execution_rows
from utk_full_domain_2026_11_01.analyze import load
from utk_full_domain_2026_11_01.profile import objdigest


def analyze_profile():
    spec=json.loads((ROOT/'PROFILE_FREEZE.json').read_text());meta=json.loads((ROOT/'results/profile-metadata.json').read_text())
    assert meta['status']=='COMPLETE' and meta['oldOutcomesReadByRunner'] is False
    assert meta['profileFreezeSha256']==digest(ROOT/'PROFILE_FREEZE.json')
    for name,sha in spec['sourceHashes'].items():assert digest(ROOT.parent/name)==sha
    assert meta['recordsSha256']==digest(ROOT/'results/profile.jsonl.gz')
    oracle=load(ROOT/'results/oracle.jsonl.gz');profile=load(ROOT/'results/profile.jsonl.gz')
    assert len(profile)==128 and [r['queryId'] for r in profile]==spec['queryIds']
    for row,p,gold in zip(execution_rows(),profile,oracle,strict=True):
        assert row['queryId']==p['queryId']==gold['queryId'];assert len(p['runs'])==4
        assert {r['method'] for r in p['runs']}==set(METHODS)
        for run in p['runs']:
            assert run['seconds']>0 and np.isfinite(run['seconds'])
            if run['status']=='exact':assert run['union']==gold['union']
            elif run['status']=='resource_unknown':assert set(gold['union'])<=set(run['union'])
            else:assert run['status']=='error'
            d=run.get('receipt',{});proof=d.get('proof')
            if run['status']!='exact' or not proof or run['method'] not in ['rsa_fd','jaa_fd']:continue
            references=[x['proof'] for x in row['receipts'].values() if x.get('status')=='exact' and 'proof' in x]
            reference=next((r for r in references if objdigest(r['filter'])==proof['filterSha256'] and objdigest(r['survivorFactors'])==proof['survivorFactorsSha256']),None)
            assert reference is not None,('New full receipt requires source expansion',p['queryId'],run['method'])
            for key in ['states','survivors','poolMapping','sourceFactorSha256']:assert proof[key]==reference[key]
            mapping=proof['poolMapping'];kept=proof['survivors']
            if run['method']=='rsa_fd':
                for j,s in proof['witnesses'].items():assert mapping[kept[int(j)]] in gold['states'][s]['top']
            else:
                covered=[]
                for cell in proof['cells']:
                    top={mapping[kept[j]] for j in cell['top']}
                    for s in cell['states']:
                        assert top==set(gold['states'][s]['top']);covered.append(s)
                assert sorted(covered)==list(range(len(gold['states'])))
    methods={}
    for method in METHODS:
        runs=[next(r for r in p['runs'] if r['method']==method) for p in profile];cost=np.array([r['seconds'] for r in runs])
        methods[method]={'queries':128,'exactQueries':sum(r['status']=='exact' for r in runs),
            'runStatuses':dict(sorted(Counter(r['status'] for r in runs).items())),
            'incompleteQueryIds':[p['queryId'] for p,r in zip(profile,runs) if r['status']!='exact'],
            'medianSeconds':float(np.median(cost)),'p95Seconds':float(np.quantile(cost,.95)),'maxSeconds':float(cost.max()),
            'capReasons':dict(sorted(Counter(r.get('receipt',{}).get('proof',{}).get('reason','unspecified') for r in runs if r['status']=='resource_unknown').items())),
            'mismatchedExactRuns':0}
    return {'status':'COMPLETE','queries':128,'allAdmissibleStates':6684,'retrospectiveSupplement':True,
            'repeats':1,'arrangementNodeCap':'disabled','wallSeconds':120,'stateScoreCellCap':50_000_000,
            'originalCppRuntimeReproduction':False,'methods':methods,'identicalFactorsLinkedToValidatedDefaultReceipts':True}


if __name__=='__main__':
    result=analyze_profile();(ROOT/'results/profile-analysis.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
