# Results and scope

Current summary: 15 November 2026. This guide describes existing evidence; it is not a new experiment or an assertion of publication readiness. Numerical records and experimental freezes remain authoritative. The scientific baseline for this documentation update is commit `33c0d031740342ef4ac4e761c70d92ac819111f1`.

## Two related tasks, two contracts

The central **retention** problem asks whether the clean-query winner stays in top-K for every allowed shared query edit. The reference scorer uses float64 character-BM25, NFC/casefold normalization and the declared finite per-token edit channel (at most 32 tokens). Shared means that the same edited query is used against every competitor. Pair bounds, affine LP, enumeration and discrete incompatibility covers provide sufficient rank bounds under documented numerical assumptions. See [theory](../round3/THEORY.md) and [retention protocol](../round3/PROTOCOL_RETENTION.md).

The complementary **possible-result union** problem extracts every document that can enter lexical top-K in a finite query domain. Pool experiments use integerized weights, NFC/lowercase normalization and their own compact full-query channel. See [offline study](../exact_pool_study/), [index-first study](../lazy_cert_study/) and [full-domain adapter mapping](../utk_full_domain_2026_11_01/METHOD_MAPPING.md). The [backend bridge](../reviewer_audit_2026_10_31/) provides measured comparisons on its declared cases; it does not prove universal equivalence between channels or scorers.

## Original retention evidence and later controls

The initial 300-query confirmation and independent 970-query replication are separate stages. Do not pool them or replace their prespecified comparisons with later favorable outcomes. Source and selection locks are in [confirmation protocol](../round3/PROTOCOL_RETENTION.md), [replication protocol](../round3/PROTOCOL_REPLICATION.md), [execution addendum](../round3/EXECUTION_ADDENDUM.md) and their frozen records.

At B=2, K=10:

| Dataset | Independent n | Audited robust | Best LP + enum | Original Discrete | Later numerical MILP + enum | Retrospective refinement |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| SciFact | 199 | 123 | 115 | 123 | 123 | 123 |
| NFCorpus | 223 | 47 | 41 | 45 | 47 | 47 |
| FiQA | 548 | 96 | 71 | 91 | 90 | 96 |
| Total | 970 | 266 | 227 | 259 | 260 | 266 |

The original LP comparison passes Holm-adjusted significance on SciFact and FiQA, not NFCorpus. Those tests do not compare Discrete with the later MILP control. All 970 IDs are joined in [query_level.csv](../codex_followup_2026_11_05/results/query_level.csv); every method disagreement is retained in [disagreement analysis](../codex_followup_2026_11_05/DISAGREEMENT_ANALYSIS.md). MILP certifies two NFCorpus cases missed by original Discrete; Discrete certifies one FiQA case missed by MILP. Numerical MILP outcomes are not exact-arithmetic certificates by themselves.

The [all-query refinement](../claims_consolidation_2026_11_01/) recovers the seven remaining audited robust cases and certifies none of the 704 audited nonrobust cases. Routing does not read robustness labels, but the refinement was designed after outcomes were available: it is retrospective. Its extra recorded cost is 121.792 seconds across the cohort, including 120.198 seconds on nonrobust cases. Original 259/260 counts and tests remain unchanged.

The controlled full-cohort runtime audit uses all 970 queries. Per-dataset paired geometric ratios of MILP time to Discrete time are approximately **1.50, 3.92 and 1.56** (SciFact, NFCorpus, FiQA) under the recorded resource limits. These are not ratios of marginal medians, universal speedups or native RSA/JAA comparisons. See [runtime exports](../codex_followup_2026_11_05/README.md) and [runtime analysis](../codex_followup_2026_11_05/RUNTIME_ANALYSIS.md). The older ten-query latency pilot remains a historical pilot.

## Follow-up validation and attribution

| Evidence | What it supports | What it does not establish |
| --- | --- | --- |
| [36-query sensitivity panel](../codex_followup_2026_11_05/ABLATION_REPORT.md): 684 fresh pipelines, 2,736 decisions | Budget, K, component and cap sensitivity with all selected queries retained | A new full-cohort confirmation or uniform component dominance |
| [Tiny exact oracle](../codex_followup_2026_11_05/): 396 checks, 185 nonvacuous positives, zero unsound tested bounds | Independent exact-dyadic checks on fully specified small domains | A formal proof of every library, full corpus or floating-point execution |
| [970-query graph replay](../self_review_2026_11_05/README.md): full 259 vs equal-weight support 250 | Nine additional decisions for the full graph prover with the same frozen prefix | 970 fresh LP/MILP runs, end-to-end timing or general monotone scheduler behavior |
| Fixed 21-weight probe: 155/285 positive Pareto checks reproved, 130 inconclusive | Some existing Pareto proofs can be recovered by tested linear supports | That all linear separators fail on unresolved checks, or a new support-only coverage result |
| Original-qrel strata: 311 positive-judgment clean winners, 659 without a positive judgment | LP/Discrete/MILP counts 145/158/160 and 82/101/100 respectively | Relevance guarantees for edited queries; unjudged does not mean irrelevant |

At B2K10 the 36-query panel gives pair/LP/Discrete/MILP coverage **11/13/15/14**; at B3K10 it gives **10/10/11/12**. Unknown/capped contexts remain in denominators. Resource-bounded first-fit graph scheduling can produce nonmonotone coverage even with a stronger edge prover; the [self-review tests and report](../self_review_2026_11_05/) retain this counterexample.

## Offline union results and failed session gate

For the declared WANDS channel, 128 queries cover 42,994 products and 6,684 query states. Every exact union matches full enumeration. Median coarse-pool size is 2,613; median exact union is 45. The original index-first construction median is 24.39 ms. In the original matched offline comparison, the paired geometric speed ratio is 2.3474 (95% bootstrap interval 2.0824–2.6293), with 107/128 wins against the faster executed per-query parent/batch control. See [index-first study](../lazy_cert_study/) and [claim matrix](../claims_consolidation_2026_11_01/CLOSEST_WORK_AUDIT.md).

| Scenario | Wins | Paired geometric speed ratio | Interpretation |
| --- | ---: | ---: | --- |
| Original matched offline construction | 107/128 | 2.3474 | Supports this offline construction comparison |
| 20 distinct requests against memo/incremental control | 38/128 | 0.7472 | Failed primary session gate |
| Repeated-request session | 1/128 | 0.4595 | Reuse does not beat memoization here |

No observed session break-even is established. Earlier projected 45/35-edit thresholds on ArguAna/SciDocs are projections, not measured break-even events. Offline gains must not be presented as interactive acceleration.

The [full finite-domain Python RSA-FD/JAA-FD controls](../utk_full_domain_2026_11_01/) produce exact results for 126/128 and 127/128 queries respectively; unresolved cases remain unknown. These are disclosed adaptations, not a full native C++ performance comparison of the original algorithms across NLP tasks. Native-output fixtures in [utk_adapter_study](../utk_adapter_study/) address a different, restricted adapter scope.

## Natural corrections and neural transfer

The measured compact-channel membership is **11/200 (5.5%) on JFLEG** and **91/200 (45.5%) on the GitHub Typo sample**. These are existing-resource correction samples, not newly collected natural search traffic and not 91% coverage. Other observed-type audits use different denominators and must be labeled separately. See [decision audits](../decision_audit_2026_10_31/) and [multiword/neural follow-up](../argon_followup_2026_11_01/).

The neural coarse-pool top-10 containment mean is 65%, with losses on 14/16 evaluated queries. Lexical-union input pairs total 67,571, equal to the memo control. Exact lexical union containment concerns lexical inputs; it does not imply preservation of full-corpus cross-encoder top-K, lower neural cost or safe RAG answers.

## Reading historical material

CAPC and BOLT are earlier classification studies with different objectives and metrics. Archived reports, logs and planning documents retain their original wording and dates; they are not the current project abstract. No evaluated CAPC/BOLT/retrieval hybrid, new human relevance labels, global SOTA claim or publication guarantee is supplied by these records.
