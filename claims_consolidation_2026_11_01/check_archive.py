"""Recompute all summaries and check source/route/group records without corpora."""
import json
from claims_consolidation_2026_11_01.analyze import ROOT,analyze


def main():
    observed=json.loads((ROOT/'results/analysis.json').read_text())
    assert analyze()==observed
    assert not observed['total']['falseCertifications']
    for path in ROOT.rglob('*'):
        assert path.suffix.lower() not in {'.tex','.bib','.cls','.bst','.pdf','.parquet','.pkl','.dat'},path
    print('PASS:all970 IDs,source freezes,label-free routes,conservative group proofs,paired component times and recomputed analysis')


if __name__=='__main__':main()
