"""Read-only follow-up receipt verification; no solver or network calls."""
import csv,gzip,hashlib,json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parent


def csvrows(name):
    with (ROOT/'results'/name).open() as f:return list(csv.DictReader(f))


def main():
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    for path,sha in freeze['code_sha256'].items():assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==sha,path
    extraction=json.loads((ROOT/'results/extraction.json').read_text())
    for path,sha in extraction['sourceFiles'].items():assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==sha,path
    q=csvrows('query_level.csv');assert len(q)==970 and len({(r['dataset'],r['query_id']) for r in q})==970
    assert Counter(r['verified_label'] for r in q)=={'ROBUST':266,'NONROBUST':704}
    for col,n in [('lp_enum_rank',227),('discrete_rank',259),('milp_enum_rank',260),('refined_rank',266)]:
        assert sum(int(r[col])<=10 for r in q)==n,col
        assert all(r['verified_label']=='ROBUST' for r in q if int(r[col])<=10),col
    assert len(csvrows('disagreement_cases.csv'))==34
    runs=[json.loads(l) for l in gzip.open(ROOT/'results/ablation_records.jsonl.gz','rt')]
    assert len(runs)==684 and len({(r['dataset'],r['query_id'],r['budget'],r['method']) for r in runs})==684
    selection=json.loads((ROOT/'selection.json').read_text());chosen={(ds,r['queryId']) for ds,rr in selection['datasets'].items() for r in rr}
    assert len(chosen)==36 and all((r['dataset'],r['query_id']) in chosen for r in runs)
    original={(r['dataset'],r['query_id']):r for r in q}
    for r in runs:
        o=original[r['dataset'],r['query_id']];assert r['query_sha256']==o['query_sha256']
        if r['budget']==2:
            col={'discrete':'discrete_rank','best_lp_enum':'lp_enum_rank'}.get(r['method'])
            if col:assert r['rank_upper']==int(o[col])
            if r['rank_upper']<=10:assert o['verified_label']=='ROBUST'
        if r['context']['status']!='ready':assert r['rank_upper']==r['context']['n']
        assert r['rss_sampled_peak_mib']>=r['rss_start_mib'] and r['rss_sample_count']>=2
        assert r['pipeline_seconds']>=r['context_seconds']>=0 and r['kernel_seconds']>=0
    assert sum(r['context']['status']=='context_resource_cap' for r in runs)==20
    decisions=csvrows('sensitivity.csv');assert len(decisions)==2736
    assert all((r['certified']=='True')==(int(r['rank_upper'])<=int(r['K'])) for r in decisions)
    cases=[json.loads(l) for l in (ROOT/'results/correctness_cases.jsonl').read_text().splitlines()]
    assert len(cases)==396 and len({r['case'] for r in cases})==12
    assert all(r['sound'] and r['rank_upper']>=r['exact_worst_rank'] for r in cases)
    assert sum(bool(r['nonvacuous_K_certificates']) for r in cases)==185
    assert all(k<r['n'] and r['exact_worst_rank']<=k for r in cases for k in r['nonvacuous_K_certificates'])
    historical=csvrows('runtime_per_query.csv');assert len(historical)==3774
    assert sum(r['repeat']=='0' for r in historical)==2910
    if (ROOT/'MANIFEST.json').exists():
        manifest=json.loads((ROOT/'MANIFEST.json').read_text())
        for path,sha in manifest['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
        for path,sha in manifest.get('inherited_source_sha256',{}).items():assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==sha,path
    print(json.dumps({'status':'PASS','original_queries':970,'new_pipelines':684,'sensitivity_decisions':2736,
                      'tiny_domain_checks':396,'nonvacuous_positive_checks':185,'historical_mutations':False}))


if __name__=='__main__':main()
