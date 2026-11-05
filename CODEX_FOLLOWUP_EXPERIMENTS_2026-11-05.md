# Codex follow-up brief — N-Gram retrieval certification experiments

**Date:** 2026-11-05  
**Target paper:** *Certifying Fixed Lexical Retrieval under Shared Query Edits*  
**Repository:** https://github.com/TruongTQ261531/N-Gram  
**Task type:** Reproduce, audit, and extend empirical evidence. Do not rewrite the paper yet.  
**Status:** This is a work order, not a report of newly completed experiments.

## 1. Mission

Strengthen the empirical case for a fixed additive character n-gram / BM25 lexical ranker whose original winner is certified to remain in top-K under a finite, shared-query token-edit budget.

Prioritize **(P1) certification-gap analysis**, **(P2) matched computational cost**, then **(P3) controlled ablations and correctness checks**. Study the negative interactive-session result only as a separate, explicitly scoped application question.

The desired outcome is a transparent decision: which claims are supported, which are not, and whether the added evidence materially strengthens an Information Processing & Management submission. Do not optimize for favorable-looking numbers.

## 2. Read these files before editing or running

Read, in this order:

1. README.md and round3/README.md
2. round3/REPRODUCE.md and round3/REPORT_VI.md
3. round3/PROTOCOL_RETENTION.md and round3/PROTOCOL_REPLICATION.md
4. round3/THEORY.md and round3/RUN_HISTORY.md
5. round3/RELATED_WORK_UPDATE.md
6. exact_pool_study/PROTOCOL.md, exact_pool_study/REPORT_VI.md, exact_pool_study/PAPER_DIRECTION.md
7. Relevant source, tests, manifests, and raw result schemas identified from those documents.

The root NEXT_STUDY.md concerns a different earlier research direction; it is **not** the plan for this retrieval-certification follow-up.

Do not assume paths or result fields beyond what actually exists. Inventory them first.

## 3. Known evidence to preserve, not silently refit

- The original 300-query confirmation and the separately locked 970-query replication are **different stages**. Never pool them to improve statistical significance.
- The independent 970-query B=2, K=10 stage contains 199 SciFact, 223 NFCorpus, and 548 FiQA queries.
- Its published best LP+enumeration counts are 115 + 41 + 71 = **227/970**.
- Its published discrete counts are 123 + 45 + 91 = **259/970**.
- The LP-to-discrete differences are 8/199, 4/223, and 20/548; only **two of three** primary comparisons pass the reported Holm adjustment. NFCorpus does not.
- Earlier manuscript work also refers to numerical MILP **260** and retrospective robustness audit **266**. **Before using these numbers, locate their actual source artifacts and establish their population, oracle, solver limits, and whether they are prospective certificates or retrospective outcomes.** The original round3 replication protocol explicitly says that generic MILP was not newly run on all 970 second-stage queries. Never present those counts as a matched full-970 prospective comparison without evidence.
- Offline possible-result union improvements and exact_pool_study are separate experiments, with a **different integer scorer / task contract** from round3 float64 retention certification. Do not combine their denominators or claim the same backend.
- Existing exact_pool_study reports that fast exact pool did **not** beat ordinary memoization on measured 5/20-request interactive sessions. Preserve that negative result.
- The finite edit channel is restricted to documented per-token delete/swap/repeat/adjacent-QWERTY alternatives and a shared budget; it does not model all natural typos, semantic preservation, or neural ranker robustness.
- Certification rate is **not** retrieval accuracy, nDCG, recall, or relevance improvement. A failure to certify means **unknown**, not necessarily nonrobust.
- LP, DP, graph cover, pruning, caching, possible-top-K unions, and equivalence reduction have prior art. Do not assert firstness or Q1 readiness.

## 4. Non-negotiable integrity rules

1. **Do not upload or commit any manuscript** (main.tex, supplementary.tex, references.bib, PDFs, title page, submission files) to the public repository. Do not search for or modify manuscript files.
2. Do not overwrite the frozen 300/970 results, manifests, selected IDs, original source locks, historical protocol files, or their checksums. Do not modify earlier CAPC/BOLT scientific artifacts.
3. Use a separate working branch and a new follow-up output directory. Never push directly to main, merge, or deploy the web app. Ask before publishing new result artifacts or opening a PR.
4. Keep original and regenerated evidence distinct; label reruns as **reproductions**, not new blind confirmations.
5. Preserve every failed, timed-out, skipped, tied, OOV, truncated, and resource-limited query with explicit status. A solver timeout or cap is not a counterexample.
6. Preserve exact query IDs and dataset provenance; do not cherry-pick queries or tune a hypothesis on already-viewed confirmation data while calling it independent.
7. Do not invent measurements, plots, p-values, speedups, oracle outputs, or literature citations. Never silently weaken numerical tolerances to make tests pass.
8. Respect data licenses; do not commit raw corpora, query texts where prohibited, private datasets, caches/pickles, or licensed full-text.
9. No paid API, GPU, human labels, or new model training is required for the core scope. If a dependency, dataset, or resource is unavailable, report it and stop the affected run.
10. Treat any additional analysis of already-viewed 970 queries as **post-hoc/exploratory**, unless a truly untouched cohort is separately locked before outcomes.

## 5. Execution plan

### Phase 0 — Repository audit and offline verification (mandatory first)

- Record Git commit SHA, branch, Python and package versions, OS, CPU, RAM, thread settings, and exact commands.
- Inventory relevant scripts, data requirements, outputs, freeze files, and existing timing fields.
- Run the documented offline verifier and round3 unit tests, preferably in a clean environment:

      python verify_all.py
      python -m unittest discover -s round3 -p 'test_*.py'

- Where appropriate, run round3/verify_archive.py and the released fixture audit in a **separate checkout** if they write diagnostics.
- Verify published per-corpus LP/discrete counts from saved per-query records, not only report text. Cross-check ID uniqueness and stage boundaries.
- Locate the source and semantics of the manuscript's MILP 260 and retrospective 266 figures. If these are unavailable or inconsistent, flag the discrepancy prominently.
- Create PHASE0_AUDIT.md with a PASS / PARTIAL / BLOCKED decision. Do not launch full expensive runs until this gate passes.

### Phase 1 — Query-level disagreement audit (highest priority)

Produce a row-level table for all 970 locked queries, without changing their outcome labels. Required fields where available:

- dataset, query ID/hash, stage, token count, edit budget, K, candidate count, clean winner score/margin;
- pair+enum, matched LP+enum, discrete, and genuinely available MILP outcomes;
- retrospective audit status **only if supported by traceable artifacts**;
- solver status, timeout/cap, enumeration completion, numerical tolerance, runtime, memory if measured;
- relevant trace features (support conflicts, graph-cover contribution, number of competitors, rank bound);
- qrel-positive status, clearly separated from certification.

Report:
- LP failure / discrete success cases by corpus and their common characteristics.
- Discrete failure / verified MILP success cases **only on the matched population where both were actually run**.
- Certificate vs retrospective-audit gap only when the retrospective oracle's definition and coverage are established.
- All unknown and capped cases separately.
- Descriptive distributions by query length, score margin, competitor count, and edit alternatives. Avoid uncorrected post-hoc significance claims.

Export query_level.csv, disagreement_cases.csv, and DISAGREEMENT_ANALYSIS.md. Include a small set of auditable traces illustrating why the methods differ.

### Phase 2 — Matched runtime and resource trade-offs

Measure or extract per-query cost for the matched LP+enum, discrete, and MILP implementations **only where comparable**. Use identical inputs, CPU quotas, thread caps, candidate sets, time limits, warm/cold definitions, and run ordering.

Record:
- wall time per stage and total, p50/p95/p99 and paired distributions;
- peak RSS or another clearly defined memory measure;
- solver calls, iterations/termination, enumeration state counts, cap/timeout rates;
- certification gain per added unit of compute;
- startup/index-building cost separately from query-time cost.

If MILP is prohibitively expensive, use a **predeclared, representative, bounded subset**, disclose the selection rule, and do not extrapolate full-population counts. An existing 1-second MILP cap is not evidence of mathematical MILP weakness; distinguish method strength from resource policy.

Produce runtime_per_query.csv, resource_profile.json, RUNTIME_ANALYSIS.md, and publication-quality plots with exact units and captions. Never claim "near-exact at lower cost" unless the matched data actually support it.

### Phase 3 — Controlled sensitivity and ablation

After Phase 0/1/2, use the implementation's supported settings to test:

- edit budgets B=1,2,3 (or the documented feasible subset);
- top-K sensitivity, e.g. K=1,5,10,20, only if supported and correctly handled;
- query length, number of token alternatives, score margin, candidate count;
- matched ablations: safe screening; pairwise margin; affine LP; support/Pareto conflict detection; discrete incompatibility cover; exact enumeration fallback.

Use an explicitly fixed sample and a recorded configuration **before** inspecting the new runs. Show both certificate gains and computational overhead. Report infeasible settings, and do not silently reduce the corpus or edit channel. Keep all such analysis exploratory unless a new independent sample is genuinely obtained and locked.

Deliver ablation.csv, sensitivity.csv, ABLATION_REPORT.md, and plots.

### Phase 4 — Independent soundness checks

On small tractable instances, independently enumerate all admissible shared-query edits and score the full relevant universe (or explicitly document the exact finite test universe). Check worst-case ties, budget accounting, OOV/all-zero scores, token multiplicity, and boundary cases.

Assert: whenever the method returns "certified", independent exhaustive checking does not find an admissible counterexample. A failed certificate is not itself an attack. Keep failing seeds, minimal reproducers, and exact configurations. If a soundness counterexample is found, **stop performance claims and report it immediately**.

Deliver correctness_cases.jsonl and SOUNDNESS_AUDIT.md.

### Phase 5 — Optional application follow-up (separate claim)

Only after core certification work is complete, analyze the offline union vs actual session-cost discrepancy using existing exact_pool_study evidence. Compare full retrieval, ordinary memoization, legacy pool, compiled pool, and exact pool with the original integer scorer and identical request sequences.

Separate index loading, factor construction, certification/projection, initialization, per-request retrieval, and cache reuse. Preserve the reported online negative findings; do not promise speedups from projected break-even estimates. Do not mix exact_pool_study's integer scorer with round3's float64 results.

This phase is optional and should not delay P1/P2.

## 6. Run policy and checkpoints

- Start immediately with read-only inspection, offline verification, and a small smoke test.
- For any step that would overwrite an existing artifact, first create a separate checkout and an external evidence backup; preferably redirect outputs to a new directory.
- Before a full 970-query recomputation or any run estimated to exceed two hours, present the estimated time, RAM, data needs, and exact command; obtain approval.
- Keep CPU/BLAS thread settings explicit and avoid concurrent heavy benchmarks.
- If baseline counts, source pins, or correctness checks disagree, pause the dependent experiment, preserve logs, and report the mismatch instead of "fixing" historical evidence.

## 7. Deliverables and directory layout

Put new work in a dedicated directory, for example:

    codex_followup_2026_11_05/
      PHASE0_AUDIT.md
      EXPERIMENT_PLAN.md
      DISAGREEMENT_ANALYSIS.md
      RUNTIME_ANALYSIS.md
      ABLATION_REPORT.md
      SOUNDNESS_AUDIT.md
      EXPERIMENT_REPORT.md
      claims_matrix.csv
      configs/
      scripts/
      results/
      plots/
      logs/
      manifests/

Adapt this layout if the repository already has a suitable research-workflow convention. Do not put new outputs into frozen round3/results or exact_pool_study/results.

EXPERIMENT_REPORT.md must include: exact commands, environment, data and sample provenance, raw result references, all methods and time limits, all positive/negative/unknown outcomes, effect sizes and uncertainty where justified, methodological limitations, and a clear GO / CONDITIONAL / NO-GO decision for strengthening the current paper.

The claims matrix must have columns:
claim | evidence | population | result | limitations | manuscript action (retain / narrow / remove / needs new experiment).

Do not edit the actual manuscript. Suggest precise text/table changes in a separate MANUSCRIPT_CHANGE_NOTES.md for the authors to review.

## 8. First response expected from Codex

1. Summarize the repository's actual relevant files and existing evidence.
2. State whether the offline verification passes.
3. Confirm which 970-query fields are already present and whether MILP 260 / retrospective 266 have traceable sources.
4. Give a ranked, resource-aware plan for the next executable experiments.
5. Execute only the inexpensive Phase 0 checks and smoke tests first. Report outputs and blockers before any expensive batch.

**Success criterion:** a reproducible, honest, query-level explanation of where discrete certification improves on LP and what it costs, with correctness checks and clearly bounded claims—not simply a larger number of runs.
