# Active confirmation protocol: discrete shared-query retention bounds

Date: 29 October 2026, Asia/Bangkok. Candidate research, not verified Q1 novelty/readiness. This protocol replaces the strict-set-invariance pilot before any confirmation metrics.

## Question and property

Can a finite-query-edit certifier provide a tighter upper rank for the clean winner than independent score bounds, exact pairwise bounds, and a shared-query convex LP, at practical CPU cost? The scorer is fixed character BM25. No improved relevance model or new benchmark is the claimed method.

For each query, certify worst-tie rank of its clean winner under a COMMON perturbed query applied to the WHOLE corpus. All score ties count ahead of the reference. Reporting rank <=K guarantees retention for any fixed tie-breaking. Primary K=10; also report K=1/5/20/50, all budgets B=1/2/3. Stability does not prove relevance or meaning preservation. Existing qrels provide only clean-query relevance context.

## Sources, selection and freezing

Use pinned BEIR SciFact, NFCorpus and FiQA, full corpora of 5183/3633/57638 documents. No hidden top-100 candidate list; documents are either safely bounded out or explicitly included. Raw corpora remain local, with source revisions/hashes in download_manifest.json.

Twenty development IDs per dataset: official dev for NFCorpus/FiQA and train for SciFact. A 100-query confirmation subset per dataset is selected from official test by SHA256(dataset|phase|query-id), before any confirmation scores. IDs are stored. Schema/count/split audits read source metadata but test metrics do not guide development. The selected test IDs have no ID or normalized-text overlap with the 20 development queries. All rows remain, including OOV/zero-score queries and ties.

Use the first 32 normalized whitespace tokens, record truncation for every query. This is a bounded-query/subset study, not full-query/full-test BEIR SOTA. Corpus title+text fits the index; query labels do not fit vocabulary, IDF, or method parameters. Keep duplicate corpus documents under their official IDs; record their counts.

Before confirmation: all unit/reference checks pass; freeze evaluation source, config, data manifest, index fingerprints, active/historical protocols and confirmation IDs; publish the freeze commit on GitHub BEFORE running test metrics. A local timestamp is not independently trusted preregistration. If a confirmation assertion fails, keep partial outputs/log and disclose any corrective rerun.

## Fixed scorer and edit model

Character ngrams 3/4/5 within whitespace tokens, space boundaries; BM25 k1=1.2, b=.75. Word BM25 is an existing-label relevance baseline. No hyperparameter search.

Per original token include raw and ALL one-operation variants: any single deletion, adjacent transposition, repeated-character insertion, or QWERTY-neighbor substitution. Deduplicate strings. At most B original tokens change and each receives at most one such operation. This is NOT an arbitrary Levenshtein ball; no semantic-equivalence assertion, general insertion, whitespace change or synonym guarantee. No new human annotation.

## Candidate and matched controls

1. Featurewise/coarse independent score bounds (safe whole-corpus screening).
2. Exact coupled pairwise margin oracle, then count every possibly outranking competitor.
3. Exhaustive counting when <=2000 allowed query states and <=2,000,000 state-by-candidate cells. Include as a strong baseline, not only toy tests.
4. Shared-query affine-envelope LP, solved by a support-oracle cutting-plane method, at most 40 cuts. Every feasible weight provides a safe bound; no convergence assumption is needed for soundness.
5. Generic compact primal LP for the SAME relaxation, when its matrix has <=2,000,000 entries. Compare quality, gap and solver cost; never presume the custom solver is faster.
6. Discrete pair-incompatibility checks: midpoint support separation, then a two-dimensional Pareto DP if needed. Cap generated points at 20000, frontier at 1000; exceeding caps returns unknown, not an edge. At most 120 pair checks, only when <=80 possible competitors. A verified clique partition yields a count bound. Candidate output is the minimum of pairwise/LP/cover/feasible-enumeration bounds.
7. Generic mixed-integer formulation for the SAME discrete count problem, with one-second HiGHS solver limit and <=2,000,000 matrix entries. Preserve all statuses, setup/solver times, feasible witness ranks and upper bounds. A timeout is unknown, not non-robust. This is a numerical comparator, not a formal proof oracle.

Run all applicable comparators on each selected query/budget. For zero-reference-score shortcuts, worst-tie rank N is attained and solver work is skipped explicitly. Solver resource skips remain visible. LP and enumeration are established methods; graph coloring and Pareto DP are established. Potential novelty lies only in a defensible specialization/combination and its demonstrated value, still subject to prior-art review.

HiGHS threads=1; one-thread numerical libraries; at most two CPU jobs concurrently. Common transpose caching applies to ALL methods. Scoring changes are not attributed to the research contribution. Build/startup costs are separate from warmed latency. Any speed claim requires isolated profiling after experimental jobs finish; development/concurrent wall times are not a latency ranking. Proposed time must include screening, LP, enumeration and graph work; comparator model-setup time must also be counted.

## Validation and uncertainty

Unit suites: exhaustive pairwise comparisons, generic primal LP vs oracle dual, Pareto incompatibility vs exhaustive choices, generic MILP vs exhaustive counts, feature factorization, exact screening vs full index, and high-precision dot-product intervals. Save all failing preparation versions and logs.

For every confirmation query, verify attained support/MIP/sample witnesses by re-encoding the complete perturbed query against the whole corpus. Three random-attack seeds 17/29/43, ten samples per seed/budget, are diagnostics ONLY and cannot certify. Every observed strict rank must be <= the proposed upper bound. The same original query is the bootstrap sampling unit across budgets/methods.

Report all datasets/budgets/K values and matched baselines. Primary scientific comparison includes pairwise+enumeration and LP+enumeration, so a trivial small-lattice enumeration gain is not mislabeled a new-method gain. Report useful coverage jointly with whether the clean winner is judged relevant; also clean nDCG@10/Recall@10 and sampled-noise nDCG diagnostics. Do not assume noisy variants preserve original qrels semantics.

Use 2000 paired query bootstrap replicates; intervals condition on these fixed corpus/index/query subsets. No independent-training or global-superiority inference. Report paired counts and multiple-comparison limits. Publication suitability and Q1 acceptance do not follow from a numerical gate or passing CI.

## Development history

The strict-set-invariance screen (20+20 queries) found zero nontrivial top-10 set certificates and was retained as a negative result. Retention was then selected on development data. Added an affine relaxation, generic LP/MILP controls, safe index screening, exact small-lattice enumeration and discrete incompatibility cover. Development also caught a sparse-metadata len() error before outputs, a missing requests import in metadata preparation (replaced with urllib), a sampled-K assertion bug before execution, and timing omissions before confirmation. None was selected using confirmation performance.
