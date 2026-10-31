"""Offline record/source consistency audit; no missing experiments invented."""
from pathlib import Path
import gzip
import hashlib
import json

ROOT=Path(__file__).resolve().parent


def rows(path):
    with gzip.open(path,'rt') as f:return [json.loads(line) for line in f]


def main():
    scope=json.loads((ROOT/'scope.json').read_text())
    for path,digest in scope['sourceFiles'].items():
        assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==digest,path
    for name in ['bridge.jsonl.gz','bridge-refined.jsonl.gz']:
        data=rows(ROOT/'results'/name)
        summary=json.loads((ROOT/'results'/(name+'.summary.json')).read_text())
        assert summary['status']=='COMPLETE' and summary['retrospective']
        assert [r['queryId'] for r in data]==scope['bridgeIds']
        assert summary['rowsSha256']==hashlib.sha256((ROOT/'results'/name).read_bytes()).hexdigest()
        assert sum(r['states'] for r in data)==summary['stateCount']==6684
        if name=='bridge.jsonl.gz':
            for key in ['stateTopKEqual','stateTransferCertified','floatBoundaryUnresolved','integerTiedStates']:
                assert sum(r[key] for r in data)==summary[key]
            assert sum(r['unionObservedEqual'] for r in data)==summary['queryUnionObservedEqual']
        else:
            for backend in ['floatLower','floatCasefold']:
                s=summary['backends'][backend]
                for key in ['stateTopKResolved','stateExactTopKEqual','stateRankResolved']:
                    assert sum(r[key][backend] for r in data)==s[key]
                assert sum(r['queryUnionCertifiedEqual'][backend] for r in data)==s['queryUnionCertifiedEqual']
                assert sum(r['worstRankIntervals'][backend]==[r['integerWorstRank']]*2 for r in data)==s['queryWorstRankEqual']
                for r in data:
                    lo,hi=r['worstRankIntervals'][backend];assert 1<=lo<=hi<=42994
                    assert r['stateExactTopKEqual'][backend]<=r['stateTopKResolved'][backend]<=r['states']
                    assert r['retentionDecisions'][backend]==(True if hi<=10 else False if lo>10 else None)
    report=json.loads((ROOT/'results/coverage_and_runtime_status.json').read_text())
    discordant=set();completed=0
    for ds,ids in scope['replicationIds'].items():
        r=report['datasets'][ds];assert r['queries']==len(ids)
        if r['supplementStatus']!='COMPLETE':
            assert r['milpCertified'] is None and r['controlledTiming'] is None
            continue
        completed+=len(ids)
        path=ROOT/'results/retention'/(ds+'.jsonl.gz');data=rows(path)
        metadata=json.loads(path.with_name(path.name+'.metadata.json').read_text())
        assert [row['queryId'] for row in data]==ids
        assert metadata['status']=='COMPLETE' and metadata['queries']==len(ids)
        assert metadata['outputSha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        assert metadata['scopeSha256']==hashlib.sha256((ROOT/'scope.json').read_bytes()).hexdigest()
        assert metadata['codeSha256']==hashlib.sha256((ROOT/'retention.py').read_bytes()).hexdigest()
        assert all(t['num_threads']==1 for t in metadata['threadpools'])
        coverage={m:0 for m in ['best_lp_enum','discrete','milp_enum']}
        for record in data:
            assert record['modelFingerprint']==metadata['modelFingerprint']
            first={run['method']:run for run in record['runs'] if run['repeat']==0}
            assert set(first)==set(coverage)
            assert first['best_lp_enum']['rankUpper']==record['oldBestLpRank']
            assert first['discrete']['rankUpper']==record['oldDiscreteRank']
            repeats=3 if record['queryId'] in scope['timingRepeatedSubset'][ds] else 1
            assert len(record['runs'])==3*repeats
            for method in coverage:
                runs=[run for run in record['runs'] if run['method']==method]
                assert sorted(run['repeat'] for run in runs)==list(range(repeats))
                assert all(run['seconds']>0 and run['rankUpper']>=1 for run in runs)
                coverage[method]+=first[method]['rankUpper']<=10
            if len({run['rankUpper']<=10 for run in first.values()})>1:
                discordant.add((ds,record['queryId']))
        assert coverage==r['supplementCoverage']
        assert r['milpCertified']==coverage['milp_enum']
    if report['status']=='COMPLETE':
        assert completed==970
        audit=json.loads((ROOT/'results/discordant_verification.json').read_text())
        assert {(r['dataset'],r['queryId']) for r in audit['records']}==discordant
        assert audit['queries']==len(audit['records'])==len(discordant)
        assert audit['enclosureCertified']==sum(r['enclosureCertifiesK10'] for r in audit['records'])
        for row in audit['records']:
            assert row['primaryBoundsAndTimesUnchanged']
            assert row['enclosureCertifiesK10']==(row['audit'].get('rankUpper',11)<=10)
        for variant in ['io-only','guard-corrected']:
            folder=ROOT/'results/native_utk'/variant
            native=json.loads((folder/'report.json').read_text())
            assert native['localVariant']==variant and not native['thirdPartyFilesRedistributed']
            for method,row in native['runs'].items():
                assert row['logSha256']==hashlib.sha256((folder/(method+'.stdout.txt')).read_bytes()).hexdigest()
                assert row['matchesContinuousUnion']==(row.get('reportedIds')==[1,2,3])
    for p in ROOT.rglob('*'):
        assert p.suffix.lower() not in {'.tex','.bib','.pdf','.cls','.bst'},p
    print('PASS: frozen inputs,128/6684 backend records,',completed,
        'complete retention queries; all missing controls remain explicit')


if __name__=='__main__':main()
