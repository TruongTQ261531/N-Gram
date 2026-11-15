"""Read-only audit of complete graph replay and fixed-grid proof diagnostics."""
from pathlib import Path
from collections import Counter
import gzip,hashlib,itertools,json
import pandas as pd

ROOT=Path(__file__).resolve().parent


def main():
    freeze=json.loads((ROOT/'FREEZE.json').read_text())
    for path,sha in freeze['source_sha256'].items():assert hashlib.sha256((ROOT.parent/path).read_bytes()).hexdigest()==sha,path
    rows=[json.loads(l) for l in gzip.open(ROOT/'results/graph_replay.jsonl.gz','rt')]
    assert len(rows)==970 and len({(r['dataset'],r['query_id']) for r in rows})==970
    ids=json.loads((ROOT.parent/'round3/results/replication_ids.json').read_text())
    assert {(r['dataset'],r['query_id']) for r in rows}=={(ds,qid) for ds,qq in ids.items() for qid in qq}
    q=pd.read_csv(ROOT.parent/'codex_followup_2026_11_05/results/query_level.csv',dtype={'query_id':str}).set_index(['dataset','query_id'])
    for r in rows:
        o=q.loc[(r['dataset'],r['query_id'])];assert r['full_rank']==o.discrete_rank and r['query_sha256']==o.query_sha256
        if r['support_rank']<=10:assert o.verified_label=='ROBUST'
        if r['zero_witness']:
            assert r['full_rank']==r['support_rank']==o.corpus_documents
            continue
        for name in ['full','support']:
            graph=r[name+'_graph'];m=r['candidate_count'];assert len(graph['checks'])<=120
            assert all(x['upper']<0 for x in graph['checks'] if x['incompatible'])
            assert r[name+'_rank']==min(r['prefix_rank'],graph['count_upper']+1)
            if graph.get('skipped'):
                assert m>80 and graph['count_upper']==m and not graph['checks'];continue
            groups=graph['groups'];assert len(groups)==graph['count_upper']
            assert sorted(v for g in groups for v in g)==list(range(m))
            edges={tuple(sorted((x['left'],x['right']))) for x in graph['checks'] if x['incompatible']}
            assert all(tuple(sorted(pair)) in edges for g in groups for pair in itertools.combinations(g,2))
            last=[g[-1] for g in groups]
            assert all(tuple(sorted(pair)) not in edges for pair in itertools.combinations(last,2))
            assert r[name+'_schedule_certificate']['compatibleCliqueWitness']==last
    assert sum(r['full_rank']<=10 for r in rows)==259
    scope=json.loads((ROOT/'LINEAR_PROBE_SCOPE.json').read_text())
    assert hashlib.sha256((ROOT/'linear_probe.py').read_bytes()).hexdigest()==scope['code_sha256']
    probe=[json.loads(l) for l in gzip.open(ROOT/'results/linear_probe.jsonl.gz','rt')]
    assert len(probe)==285 and len({(r['dataset'],r['query_id'],r['left'],r['right']) for r in probe})==285
    assert {(r['dataset'],r['query_id']) for r in probe}=={(ds,qid) for ds,qq in scope['query_ids'].items() for qid in qq}
    for r in probe:
        assert r['original_pareto_upper']<0 and len(r['tested'])==21
        assert [x['lambda'] for x in r['tested']]==scope['lambda_grid']
        assert min(r['tested'],key=lambda x:x['outward_upper'])['outward_upper']==r['best_outward_upper']
        assert r['grid_support_proves_incompatible']==(r['best_outward_upper']<0)
        assert next(x['outward_upper'] for x in r['tested'] if x['lambda']==.5)>=0
    assert sum(r['grid_support_proves_incompatible'] for r in probe)==155
    linear=json.loads((ROOT/'results/linear_probe_summary.json').read_text());assert linear['existing_partitions_linearly_certifiable']==3
    assert sum(r['within_group_pareto_pairs'] for r in linear['rows'])==172
    assert sum(r['within_group_pareto_grid_unresolved'] for r in linear['rows'])==76
    strata=pd.read_csv(ROOT/'results/qrel_strata.csv')
    positive=strata[(strata.dataset=='TOTAL')&strata.positive_original_qrel].iloc[0]
    assert (positive.queries,positive.lp_certified,positive.full_certified,positive.milp_certified)==(311,145,158,160)
    if (ROOT/'MANIFEST.json').exists():
        manifest=json.loads((ROOT/'MANIFEST.json').read_text())
        for path,sha in manifest['sha256'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==sha,path
    print(json.dumps({'status':'PASS','queries':970,'default_rank_mismatches':0,'false_support_certifications_K10':0,
                      'Pareto_edges_probed':285,'grid_linear_proofs':155,'positive_qrel_queries':311}))


if __name__=='__main__':main()
