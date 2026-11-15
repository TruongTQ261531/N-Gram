"""Post-run joins only: counterfactual graph receipts, labels and original qrels."""
from pathlib import Path
import gzip,hashlib,json,re
import pandas as pd

ROOT=Path(__file__).resolve().parent


def main():
    rows=[json.loads(l) for l in gzip.open(ROOT/'results/graph_replay.jsonl.gz','rt')]
    assert len(rows)==970
    q=pd.read_csv(ROOT.parent/'codex_followup_2026_11_05/results/query_level.csv',dtype={'query_id':str})
    records=[]
    lookup=q.set_index(['dataset','query_id'])
    for r in rows:
        o=lookup.loc[(r['dataset'],r['query_id'])]
        assert r['query_sha256']==o.query_sha256 and r['full_rank']==o.discrete_rank
        assert not (r['support_rank']<=10 and o.verified_label=='NONROBUST')
        z={k:r[k] for k in ['dataset','query_id','full_rank','support_rank','status','candidate_count','context_seconds']}
        z.update(qrel_positive=bool(o.qrel_positive),verified_label=o.verified_label,lp_rank=int(o.lp_enum_rank),milp_rank=int(o.milp_enum_rank),refined_rank=int(o.refined_rank))
        for name in ['full','support']:
            graph=r.get(name+'_graph',{});checks=graph.get('checks',[])
            z[name+'_checks']=len(checks);z[name+'_proved_edges']=sum(c['incompatible'] for c in checks)
            z[name+'_pareto_edges']=sum(c['incompatible'] and c['method']=='pareto' for c in checks)
            z[name+'_graph_seconds']=r.get(name+'_graph_seconds');z[name+'_graph_skip']=graph.get('skipped')
        records.append(z)
    a=pd.DataFrame(records);assert len(a[['dataset','query_id']].drop_duplicates())==970
    a.to_csv(ROOT/'results/query_graph_comparison.csv',index=False)
    coverage=[]
    for ds in ['scifact','nfcorpus','fiqa','TOTAL']:
        g=a if ds=='TOTAL' else a[a.dataset==ds]
        for k in [1,5,10,20]:
            coverage.append({'dataset':ds,'K':k,'queries':len(g),'full_certified':int((g.full_rank<=k).sum()),'support_certified':int((g.support_rank<=k).sum()),
                             'full_only':int(((g.full_rank<=k)&(g.support_rank>k)).sum()),'support_only':int(((g.full_rank>k)&(g.support_rank<=k)).sum())})
    pd.DataFrame(coverage).to_csv(ROOT/'results/coverage.csv',index=False)
    stratified=[]
    for ds in ['scifact','nfcorpus','fiqa','TOTAL']:
        g=a if ds=='TOTAL' else a[a.dataset==ds]
        for flag in [True,False]:
            z=g[g.qrel_positive==flag]
            row={'dataset':ds,'positive_original_qrel':flag,'queries':len(z)}
            for name in ['lp','full','support','milp','refined']:row[name+'_certified']=int((z[name+'_rank']<=10).sum())
            row['full_gain_over_lp']=int(((z.full_rank<=10)&(z.lp_rank>10)).sum());stratified.append(row)
    pd.DataFrame(stratified).to_csv(ROOT/'results/qrel_strata.csv',index=False)
    discordant=a[((a.full_rank<=10)&(a.support_rank>10))|((a.full_rank>10)&(a.support_rank<=10))]
    discordant.to_csv(ROOT/'results/full_support_disagreements_K10.csv',index=False)
    mechanism=pd.read_csv(ROOT.parent/'round3/results/mechanism_query_audit.csv',dtype={'query_id':str})
    gain=mechanism[(mechanism.stage=='independent')&mechanism.gain]
    assert len(gain)==32 and gain.generic_lp_success.all()
    numerical={'gain_queries':32,'generic_LP_reported_objective_min':float(gain.generic_lp_objective.min()),
               'generic_LP_reported_objective_max':float(gain.generic_lp_objective.max()),
               'certification_count_threshold':10,'raw_objectives_below_threshold_by_1e_6':int((gain.generic_lp_objective<10-1e-6).sum()),
               'interpretation':'numerical objective diagnostic, not a formal primal/dual certificate'}
    selected=a[(a.full_rank<=10)&(a.lp_rank>10)]
    summary={'queries':970,'replayed_default_rank_mismatches':0,'false_support_K10_certifications':0,
             'full_K10':int((a.full_rank<=10).sum()),'support_K10':int((a.support_rank<=10).sum()),
             'full_only_K10':[{'dataset':r.dataset,'query_id':r.query_id,'full_rank':int(r.full_rank),'support_rank':int(r.support_rank),'qrel_positive':bool(r.qrel_positive)} for _,r in a[(a.full_rank<=10)&(a.support_rank>10)].iterrows()],
             'support_only_K10':[{'dataset':r.dataset,'query_id':r.query_id,'full_rank':int(r.full_rank),'support_rank':int(r.support_rank),'qrel_positive':bool(r.qrel_positive)} for _,r in a[(a.full_rank>10)&(a.support_rank<=10)].iterrows()],
             'original32_LP_gains_also_certified_by_support':int((selected.support_rank<=10).sum()),
             'numerical_LP_diagnostic':numerical,'coverage':coverage,'qrel_strata':stratified,
             'scope':'retrospective graph-only replay with shared frozen pair/custom-LP/enum prefix;no new full-pipeline solver timing'}
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    probes=[json.loads(l) for l in gzip.open(ROOT/'results/linear_probe.jsonl.gz','rt')]
    mapped={(r['dataset'],r['query_id'],r['left'],r['right']):r for r in probes};partitions=[]
    for ds in ['scifact','nfcorpus','fiqa']:
        with gzip.open(ROOT.parent/'round3/results'/(ds+'_independent_replication.jsonl.gz'),'rt') as f:old={r['query_id']:r for r in map(json.loads,f)}
        for qid in sorted({r['query_id'] for r in probes if r['dataset']==ds}):
            import itertools
            graph=old[qid]['proposed_details']['graph_certificate'];checks={(r['left'],r['right']):r for r in graph['checks']}
            needed=[tuple(sorted(pair)) for g in graph['groups'] for pair in itertools.combinations(g,2)]
            pareto=[pair for pair in needed if checks[pair]['method']=='pareto']
            unresolved=[pair for pair in pareto if not mapped[(ds,qid,*pair)]['grid_support_proves_incompatible']]
            partitions.append({'dataset':ds,'query_id':qid,'within_group_pairs':len(needed),'within_group_pareto_pairs':len(pareto),
                               'within_group_pareto_grid_unresolved':len(unresolved),'original_partition_certifiable_with_grid_linear_support':not unresolved})
    linear={'scope':'retrospective proof-replacement diagnostic of all32 original LP gain cases;not a new end-to-end algorithm',
            'queries':32,'checked_pareto_edges':len(probes),'grid_linear_recovered':sum(r['grid_support_proves_incompatible'] for r in probes),
            'grid_unresolved':sum(not r['grid_support_proves_incompatible'] for r in probes),
            'existing_partitions_linearly_certifiable':sum(r['original_partition_certifiable_with_grid_linear_support'] for r in partitions),
            'within_group_pareto_pairs':sum(r['within_group_pareto_pairs'] for r in partitions),
            'within_group_pareto_grid_unresolved':sum(r['within_group_pareto_grid_unresolved'] for r in partitions),'rows':partitions,
            'limitations':'Grid failure is inconclusive about the optimal separating weight. Frozen partitions were chosen by the full prover; linear recertification does not imply a support-only scheduler finds them or has the same cost.'}
    (ROOT/'results/linear_probe_summary.json').write_text(json.dumps(linear,indent=2)+'\n')
    for p in (ROOT/'results').glob('*.csv'):p.write_bytes(p.read_bytes().replace(b'\r\n',b'\n'))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
