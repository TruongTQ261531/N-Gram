"""Deterministic post-run analysis; original primary artifacts stay untouched."""
import csv,gzip,hashlib,json,platform
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'


def main():
    q=pd.read_csv(OUT/'query_level.csv',dtype={'query_id':str})
    # The extractor's empty-detail fallback is not an executed enumeration.
    q.loc[q.zero_witness,'enumeration_status']='not_run_zero_witness'
    q.to_csv(OUT/'query_level.csv',index=False)
    records=[json.loads(l) for l in gzip.open(OUT/'ablation_records.jsonl.gz','rt')]
    assert len(records)==684
    keys=[(r['dataset'],r['query_id'],r['budget'],r['method']) for r in records]
    assert len(set(keys))==684
    labels=q.set_index(['dataset','query_id']);rows=[];sens=[]
    mismatches=[]
    for r in records:
        c=r['context'];d=r['detail'];g=d.get('graph',{});st=d.get('stages',{});identity=(r['dataset'],r['query_id'])
        row={k:r[k] for k in ['dataset','query_id','budget','method','rank_upper','used_tokens','context_seconds','kernel_seconds','pipeline_seconds','rss_start_mib','rss_sampled_peak_mib','rss_sample_count','process_cumulative_hwm_mib']}
        row.update(status=c['status'],certified_K10=r['rank_upper']<=10,planned_dense_cells=c['scoreCellsPlanned'],
                   materialized_documents=c['materializedDocuments'],candidate_count=c.get('candidateCount'),
                   graph_checks=len(g.get('checks',[])),graph_rank=g.get('count_upper',0)+1 if 'count_upper' in g else None,
                   support_edges=sum(x['incompatible'] and x['method']=='support' for x in g.get('checks',[])),
                   pareto_edges=sum(x['incompatible'] and x['method']=='pareto' for x in g.get('checks',[])),
                   graph_skip=g.get('skipped'),enumeration_status=d.get('enumeration',{}).get('skipped','complete' if 'enumeration' in d else 'not_run'),
                   milp_status=d.get('MILP',{}).get('status'),milp_gap=d.get('MILP',{}).get('gap'),milp_skip=d.get('MILP',{}).get('skipped'))
        for name in ['querySeconds','screenSeconds','materializeSeconds','pairIntervalSeconds']:row[name]=c.get(name)
        for name in ['enumeration','customLP','genericLP','graph','MILP']:row[name+'_seconds']=st.get(name)
        if r['budget']==2:
            original=labels.loc[identity];row['original_B2_label']=original.verified_label
            assert not (row['certified_K10'] and original.verified_label=='NONROBUST'),identity
            column={'discrete':'discrete_rank','best_lp_enum':'lp_enum_rank'}.get(r['method'])
            if column and r['rank_upper']!=int(original[column]):mismatches.append((identity,r['method'],r['rank_upper'],int(original[column])))
        rows.append(row)
        for k in [1,5,10,20]:sens.append({**{x:row[x] for x in ['dataset','query_id','budget','method','rank_upper','status']},'K':k,'certified':r['rank_upper']<=k,'timing_policy':'K-independent bound threshold;not another execution'})
    assert not mismatches,mismatches
    a=pd.DataFrame(rows);a.to_csv(OUT/'ablation.csv',index=False);pd.DataFrame(sens).to_csv(OUT/'sensitivity.csv',index=False)
    # Summaries include every selected query and every executed cap outcome.
    summary=a[a.budget==2].groupby('method').agg(n=('query_id','size'),certified_K10=('certified_K10','sum'),
             median_seconds=('pipeline_seconds','median'),p95_seconds=('pipeline_seconds',lambda s:s.quantile(.95)),
             capped_contexts=('status',lambda s:(s=='context_resource_cap').sum()),max_sampled_process_rss_mib=('rss_sampled_peak_mib','max'))
    summary.to_csv(OUT/'ablation_summary.csv')
    pd.DataFrame(sens).groupby(['budget','K','method']).agg(n=('query_id','size'),certified=('certified','sum')).to_csv(OUT/'sensitivity_summary.csv')
    history=pd.read_csv(OUT/'runtime_per_query.csv',dtype={'query_id':str});first=history[history.repeat==0]
    assert len(first)==2910 and len(first[['dataset','query_id','method']].drop_duplicates())==2910
    historic=first.groupby(['dataset','method']).seconds.agg(n='size',median='median',p95=lambda s:s.quantile(.95),p99=lambda s:s.quantile(.99),minimum='min',maximum='max')
    historic.to_csv(OUT/'runtime_summary_970.csv')
    disagreements=q[q.lp_to_discrete_gain|q.discrete_fail_milp_success|q.discrete_success_milp_fail].copy()
    disagreements['diagnostic_status']='posthoc;all coverage disagreements retained;not causal inference'
    disagreements['explanation']=np.where(disagreements.discrete_fail_milp_success,
        'MILP status optimal; capped first-fit graph/LP insufficient; enumeration resource cap',
        np.where(disagreements.discrete_success_milp_fail,'cover certifies; numerical MILP time limit retains weaker bound; enumeration resource cap',
                 'discrete cover adds coverage despite a successful generic LP solve; proof/schedule details in traces'))
    disagreements.to_csv(OUT/'disagreement_cases.csv',index=False)
    assert len(disagreements)==34
    pivot=a[a.budget==2].pivot(index=['dataset','query_id'],columns='method',values='rank_upper')
    def gain(x,y):return [f'{ds}:{qid}' for ds,qid in pivot.index[(pivot[x]<=10)&(pivot[y]>10)]]
    budget_counts={str(b):a[(a.budget==b)&a.method.isin(['pair_enum','best_lp_enum','discrete','milp_enum'])].groupby('method').certified_K10.sum().astype(int).to_dict() for b in [1,2,3]}
    details={'rows':684,'queries':36,'sensitivity_rows':len(sens),'default_LP_Discrete_rank_mismatches':0,
             'no_screen_context_caps':a[(a.method=='discrete_no_screen')&(a.status=='context_resource_cap')].query_id.tolist(),
             'all_context_caps':int((a.status=='context_resource_cap').sum()),'B2K10_counts':summary.certified_K10.astype(int).to_dict(),
             'B_K10_counts':budget_counts,'discrete_over_best_lp':gain('discrete','best_lp_enum'),
             'full_over_support_only':gain('discrete','discrete_support_only'),
             'discrete_no_lp_differences':int((pivot.discrete!=pivot.discrete_no_lp).sum()),
             'discrete_no_enum_differences':int((pivot.discrete!=pivot.discrete_no_enum).sum()),
             'K20_support_only_over_full':[f'{ds}:{qid}' for ds,qid in pivot.index[(pivot.discrete_support_only<=20)&(pivot.discrete>20)]],
             'soundness':json.loads((OUT/'soundness_summary.json').read_text())}
    (OUT/'analysis_summary.json').write_text(json.dumps(details,indent=2)+'\n')
    (ROOT/'DISAGREEMENT_ANALYSIS.md').write_text('''# Complete-cohort disagreement audit\n\nAll 970 IDs join successfully. LP=227, Discrete=259, later MILP=260; labels are 266 ROBUST/704 NONROBUST. All 32 Discrete gains over LP have successful generic LP solves. The union of LP/Discrete/MILP coverage disagreements has 34 queries. This is an all-case retrospective diagnostic, not outcome-based sampling of a new benchmark.\n\n- NFCorpus PLAIN-2240: pair/LP/Discrete/MILP ranks 26/23/12/7.\n- NFCorpus PLAIN-1141: 40/36/22/9.\n- FiQA 5369: 24/19/8/13; numerical MILP time limit, reported gap 0.714286.\n\nBoth NFCorpus numerical MILP solves report optimal status; exact enumeration is resource-capped in all three disagreements. Neither caps nor LP failures explain away all opposing results. More complete pair construction in the existing retrospective refinement recovers the two NFCorpus cases, at the disclosed extra cost. The original method remains 259 vs 260. Graph checks, support/Pareto proof receipts, margins, alternatives and lengths accompany all cases in CSV/gzip traces.\n\nLP-gain queries have median 12.5 retained tokens and 14 screened competitors, versus 9 and 120 in the remaining 938 queries. These are descriptive posthoc differences, confounded by difficulty and resource limits; they do not establish a causal length or margin effect. Only 13 gain winners have positive qrels.\n''')
    (ROOT/'RUNTIME_ANALYSIS.md').write_text('''# Cost and memory interpretation\n\nThe complete archived first pass contributes 2,910 whole-pipeline runs (970 per method). Its 3,774 total rows also include repeated subsets, retained separately. runtime_summary_970.csv uses repeat=0 only and reports p50/p95/p99/min/max with no completed-only filtering. Historic per-stage times and method-local peak RSS were not recorded; they remain explicitly missing.\n\nThe new 684 executions have fresh query construction/screening/materialization/pair intervals and separate kernel stages. Only the immutable warm index is shared. One numerical thread and deterministic hash order are used; one pass is exploratory, with no paired speed significance claims. CPU quota is four and memory limit 32GiB. Shared-host noise, allocator retention and a short small-domain validation process during the study are not controlled away.\n\nProcess RSS is sampled every 20ms plus stage endpoints, including the resident index and retained allocator pages. It is a sampled process footprint, not exact method-local peak or an estimate of private marginal allocation. OS cumulative HWM is a separate column and is never relabeled as per-method memory. Max sampled footprint is %.1f MiB.\n\nThe new common 20M dense-cell cap is additional to original solver caps. All 20 capped executions remain in denominators as full-corpus-rank unknowns. Eight are no-screen B=2 FiQA pipelines. Their lower incurred times cannot be used as a speed win because they skip materialization and lose output completeness. Source/model loading are excluded from warm-index pipeline costs.\n'''%a.rss_sampled_peak_mib.max())
    (ROOT/'ABLATION_REPORT.md').write_text('''# Retrospective 36-query component/budget panel\n\nSelection: 12 per corpus, three hash-selected IDs per token-length quartile, without outcome-based filtering. FREEZE.json predates outcomes. This remains retrospective because the 970-query cohort and method behavior were already studied. All 684 pipelines finish; 20 return explicit context-cap unknowns. Original B=2 Best-LP and Discrete rank bounds match on all 36 cases.\n\nAt B=2,K=10: pair+enum 11/36; Best LP+enum 13; Discrete 15; support-only graph 14; Discrete without LP 15; without enumeration 15; MILP+enum 14. Custom-LP+enum alone also gives 13. Thus the graph has an incremental observed effect over LP and one full-Pareto/schedule gain over support-only. Neither LP nor feasible enumeration adds K=10 coverage after the graph on this small panel, although LP tightens 12 rank bounds and enumeration tightens one. Do not claim every component is necessary for the binary decision.\n\nAt B=2,K=20, support-only certifies 19 vs full Discrete 18. Pair-proof changes affect the resource-bounded first-fit/check schedule; a stronger pair oracle does not guarantee a stronger capped final cover. This adverse scheduling result is retained and the data do not support monotonic coverage dominance by the full Pareto layer.\n\nAt K=10 and B=1, all four principal methods certify 28/36. At B=3, pair/LP/Discrete/MILP certify 10/10/11/12, including three common context caps per method. This counterexample to uniform dominance is retained. Thresholding the same K-independent bounds at K=1,5,10,20 gives 2,736 decision rows, not four new timing runs. No new significance tests or confirmatory p-values are claimed.\n\nRemoving screening reaches the added context cap on 8/36 FiQA cases and certifies 13 vs 15. This shows a resource/completeness boundary; cap-shortened execution time is not a runtime advantage. See RUNTIME_ANALYSIS.md for sampled RSS and unmatched historical metrics. All per-query records and proof receipts remain available.\n''')
    (ROOT/'SOUNDNESS_AUDIT.md').write_text('''# Independent tiny-domain arithmetic audit\n\nPASS: 12 full synthetic domains, 16 documents each, 11 configurations x 3 budgets = 396 method-budget checks, zero bounds below exact worst rank. 185 checks yield at least one nonvacuous positive certificate at K=1/5/10 (<16). Complete ties, OOV/all-zero, empty deletion, repeated positions, casefolding, stable winners and three-position channels are included.\n\nThe oracle manually counts NFC/casefold character 3/4/5-grams and accumulates stored float64 coefficients as unbounded dyadic integers. It enumerates the Cartesian product and counts changed positions without the certifier DP, sparse scoring or graph. Channel generation and stored index construction still define the shared contract; this is not independent training or a formal compiled-library proof. Tiny-domain success does not supply new full-corpus ground truth. Raw cases and worst-state witnesses are in results/correctness_cases.jsonl. The previous 1,200 exhaustive and 210 high precision checks remain unchanged.\n''')
    profile={'cpu_max':Path('/sys/fs/cgroup/cpu.max').read_text().strip(),'memory_max_bytes':Path('/sys/fs/cgroup/memory.max').read_text().strip(),
             'platform':platform.platform(),'python':platform.python_version(),'sampling_seconds':.020,'method_memory_scope':'sampled process RSS including immutable index;not isolated marginal memory','max_sampled_rss_mib':float(a.rss_sampled_peak_mib.max()),'runtime_rows_historical':len(history),'runtime_first_pass_rows_historical':len(first),'new_pipeline_rows':684}
    (OUT/'resource_profile.json').write_text(json.dumps(profile,indent=2)+'\n')
    claims=[('retention_vs_LP','supported_scope','locked970:259 vs227;two of three Holm tests','fixed scorer/channel;not relevance or global LP superiority'),
            ('retention_vs_MILP','no_uniform_dominance','259 vs260;B3 new panel11 vs12','capped numerical reference;native dual proof not supplied'),
            ('component_necessity','partial_only','graph15 vsLP13;support-only14;noLP/noenum both15','36 retrospective queries;not all components necessary'),
            ('all_query_refinement','retrospective_supported','266 robust certified;0/704 nonrobust;121.792 extra seconds','not new confirmation;171 nonrobust routes consume120.198 seconds'),
            ('offline_union','supported_scope','original paired geometric ratio2.3474','original controls only;integer compact channel'),
            ('session_speed','failed','38/128;ratio0.7472;repeated1/128','no online acceleration or measured break-even'),
            ('neural_transfer','input_only','lexical cascade same pairs67571;coarse top10 containment65%','no neural topK/RAG guarantee or matched neural savings'),
            ('dataset_novelty','not_claimed','computational labels on inherited corpora','not new natural queries or human annotations'),
            ('soundness','conditional_supported','396 tiny-domain checks;185 nonvacuous positive outcomes','stored weights/channel;not formal library proof'),
            ('IPM_novelty','editorial_judgment','scoped specialization plus empirical contract audit','no guarantee of priority, desk-review or acceptance')]
    pd.DataFrame(claims,columns=['claim','status','evidence','boundary']).to_csv(OUT/'claims_matrix.csv',index=False)
    # Canonical LF exports keep Git blobs and checked-out receipt hashes equal.
    for path in OUT.glob('*.csv'):
        path.write_bytes(path.read_bytes().replace(b'\r\n',b'\n'))
    print(json.dumps(details,indent=2));print(summary.to_string())


if __name__=='__main__':main()
