"""Check source identities, segment witnesses, native outputs and analysis.

Original whole-corpus exclusions and chosen state scores additionally require
replay from pinned WANDS inputs; this archive check does not pretend to do that.
"""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
from reviewer_audit_2026_10_31.native_utk import parse_ids
from utk_adapter_study.adapter import endpoints, point_text
from utk_adapter_study.analyze import summary

ROOT=Path(__file__).resolve().parent


def verify_witnesses(a,b,witnesses,pool,k=10):
    local={int(j):i for i,j in enumerate(pool)}
    for document, pair in witnesses.items():
        j=local[int(document)]; t=Fraction(*pair)
        assert 0<=t<=1
        # Cross-multiplication with unbounded integers, independent of oracle events.
        scores=[(t.denominator-t.numerator)*int(x)+t.numerator*int(y) for x,y in zip(a,b)]
        assert sum(s>scores[j] for s in scores)<k, (document,pair)


def main():
    with gzip.open(ROOT/'results/records.jsonl.gz','rt') as f: rows=[json.loads(s) for s in f]
    with gzip.open(ROOT.parent/'lazy_cert_study/results/confirmation.jsonl.gz','rt') as f:
        old=[json.loads(s) for s in f]
    assert [r['queryId'] for r in rows]==[r['queryId'] for r in old]
    meta=json.loads((ROOT/'results/metadata.json').read_text())
    assert meta['recordsSha256']==hashlib.sha256((ROOT/'results/records.jsonl.gz').read_bytes()).hexdigest()
    assert meta['protocolSha256']==hashlib.sha256((ROOT/'PROTOCOL.md').read_bytes()).hexdigest()
    for name, sha in meta['codeHashes'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==sha
    replay=json.loads((ROOT/'results/source-replay.json').read_text())
    assert replay['status']=='PASS' and replay['queries']==128
    assert replay['recordsSha256']==meta['recordsSha256']
    assert replay['modelHash']==replay['independentArrayDigest']==old[0]['modelHash']
    for row, archived in zip(rows,old):
        assert row['querySha256']==archived['querySha256']
        assert row['originalFullLatticeUnion']==archived['oracleUnion']
        assert len(row['state'])==row['tokens'] and sum(s!=0 for s in row['state'])<=2
        pool=row['pool']; a=np.array(row['originalA'],dtype=np.int64); b=np.array(row['originalB'],dtype=np.int64)
        assert len(pool)==len(set(pool))==len(a)==len(b)
        embed=row['embedding']; shift=embed['commonIntegerShift']; power=embed['scalePower']
        coords=np.rint(np.column_stack((3*b-a+shift,3*a-b+shift))*(2.0**(24-power))).astype(np.int64)
        ea=coords[:,0]+3*coords[:,1]; eb=3*coords[:,0]+coords[:,1]
        assert ea.tolist()==row['exportA'] and eb.tolist()==row['exportB']
        assert hashlib.sha256(point_text(coords).encode()).hexdigest()==row['nativePointsSha256']
        for key in ('originalScreen','exportScreen'):
            receipt=row[key]; maximum=receipt['maximumExcludedUpper']
            assert maximum is None or maximum<receipt['threshold']
        assert [pool[i] for i in endpoints(a,b,10)]==row['endpointUnion']
        if row['oracleStatus']!='EXACT': continue
        for prefix, x, y in [('original',a,b),('export',ea,eb)]:
            witnesses=row[prefix+'SegmentWitnesses']
            assert sorted(map(int,witnesses))==row[prefix+'SegmentUnion']
            verify_witnesses(x,y,witnesses,pool)
        assert set(row['endpointUnion'])<=set(row['originalSegmentUnion'])
        assert row['extraOverEndpoints']==sorted(set(row['originalSegmentUnion'])-set(row['endpointUnion']))
        assert row['extraOverFullFiniteLattice']==sorted(set(row['originalSegmentUnion'])-set(archived['oracleUnion']))
        for method, run in row['runs'].items():
            log=ROOT/'results'/(row['queryId']+'-'+method+'.stdout.txt')
            assert hashlib.sha256(log.read_bytes()).hexdigest()==run['logSha256']
            if run['status']=='EXITED':
                assert [j-1 for j in parse_ids(log.read_text())]==run['reportedLocalIds']
                reported=run['reportedGlobalIds']; expected=row['exportSegmentUnion']
                assert run['missing']==sorted(set(expected)-set(reported))
                assert run['extra']==sorted(set(reported)-set(expected))
                assert run['matchesExportOracle']==(not run['missing'] and not run['extra'] and not run['invalidIds'])
    assert summary(rows)==json.loads((ROOT/'results/analysis.json').read_text())
    print('PASS: 128 selections, dyadic exports, rational attaining witnesses, native logs and analysis')


if __name__=='__main__': main()
