"""Recompute adapter summaries and verify all recorded state/cell receipts."""
import json,math
from utk_full_domain_2026_11_01.analyze import ROOT,analyze
from utk_full_domain_2026_11_01.run import digest
from utk_full_domain_2026_11_01.analyze_profile import analyze_profile


def main():
    result,_,_=analyze()
    def compare(a,b):
        if isinstance(a,float):assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-12)
        elif isinstance(a,dict):
            assert a.keys()==b.keys()
            for key in a:compare(a[key],b[key])
        elif isinstance(a,list):
            assert len(a)==len(b)
            for x,y in zip(a,b):compare(x,y)
        else:assert a==b
    compare(result,json.loads((ROOT/'results/analysis.json').read_text()))
    compare(analyze_profile(),json.loads((ROOT/'results/profile-analysis.json').read_text()))
    source=json.loads((ROOT/'results/source_audit.json').read_text())
    assert source['status']=='PASS' and source['queries']==128 and source['states']==6684
    assert source['scriptSha256']==digest(ROOT/'audit_sources.py')
    assert [r['queryId'] for r in source['records']]==json.loads((ROOT/'FREEZE.json').read_text())['queryIds']
    for path in ROOT.rglob('*'):
        assert path.suffix.lower() not in {'.tex','.bib','.cls','.bst','.pdf','.parquet','.pkl','.dat'},path
    print('PASS:128queries,all6684states,allrepeats,strict dominance receipts,full-corpus oracle,JAA equality cells,source freeze and analysis')


if __name__=='__main__':main()
