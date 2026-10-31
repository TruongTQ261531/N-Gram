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
    for ds,ids in scope['replicationIds'].items():
        r=report['datasets'][ds];assert r['queries']==len(ids)
        if r['supplementStatus']!='COMPLETE':
            assert r['milpCertified'] is None and r['controlledTiming'] is None
    for p in ROOT.rglob('*'):
        assert p.suffix.lower() not in {'.tex','.bib','.pdf','.cls','.bst'},p
    print('PASS: frozen inputs,128/6684 backend records, summaries and explicit unmeasured controls')


if __name__=='__main__':main()
