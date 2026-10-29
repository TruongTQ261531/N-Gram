# Independent second-stage replication, before new-query metrics

This protocol is written after inspecting the original 300-query confirmation. Those results remain a separate stage, with all confidence intervals and the full 18-comparison Holm adjustment preserved. They are NOT pooled with this stage to manufacture significance.

## Reason and fixed hypothesis

The original B2/K10 gain over best LP+enumeration was +5/+4/+5 percentage points on SciFact/NFCorpus/FiQA (n=100 each), but exact paired evidence after multiplicity adjustment was insufficient. Run an independent replication using ALL remaining, previously unevaluated official test query inputs. The target chosen from stage 1 is B=2, K=10, proposed discrete certificate versus best shared-query LP plus feasible exhaustive enumeration. Three dataset-specific tests, Holm family size=3, alpha=.05, two-sided exact paired tests. Also report differences versus pairwise+enumeration descriptively. Fixed sample sizes are all eligible fresh inputs, with no sequential stopping.

## Independence and selection

Exclude every previously evaluated development20 and primary100 query ID. Exclude effective input text (NFC/casefold/whitespace, first32 tokens) matching any previously evaluated input; deduplicate remaining effective inputs deterministically. Iterate official test IDs in SHA256(dataset|replication|query-id) order, independent of relevance or scores. Store exact fresh IDs, exclusions and counts before execution. Nominal maximum before text exclusions is 200+223+548=971 queries. Keep OOV/tie/zero-score queries; do not filter by quality or certificate.

The public retrieval corpora and source revisions are unchanged; no new model is fitted or parameter selected. Original qrels are existing labels and do not drive the method. Index fingerprints remain fixed. Corpora are reused because the target is new QUERIES, not new-corpus generalization. This stage does not claim unseen-language transfer.

## Method identity and implementation

The mathematical predictor and all parameters remain those frozen at commit 8dd7972dc13d85159e908f9b6ea03c394289acd2: same scorer, edit states, 32-token cap, 40 cuts, 120 graph checks, candidate80/front1000/points20000 limits and enumeration/resource caps. No tuning after the first confirmation.

Use the budget_max=2 implementation adapter in replay.py to avoid constructing irrelevant B3 work. Before new-query scoring, check this adapter against all300 original B2 profiles under controlled one-thread execution. Publish this protocol, the exact new source/IDs/freeze and a digest of the original evidence BEFORE new-query metrics. New source includes optional proof export only; no method parameter changes.

For each fresh query run the proposed certificate and generic compact LP on the SAME problem when within its predeclared resource cap. The strongest LP baseline takes the best valid bound from custom/generic LP and feasible enumeration; if generic LP is unavailable, preserve the recorded custom/cheap valid bounds. Do not count resource skips as negative robustness. Save every query, all returned LP/graph/enumeration certificates, numerical solver outcomes, actual support-witness operations/rank, and original clean-query relevance metrics. No human annotation or LLM judge is introduced.

The generic MILP reference and 27000 individual sampled attacks were already run in the first confirmation. They are not newly claimed as run for all second-stage queries. This replication focuses on the selected structural improvement and its uncertainty. Concurrency is at most two workers, with BLAS and HiGHS explicitly one-thread; timings here are not isolated latency benchmarks.

## Analysis and interpretation

Analyze this stage separately. Paired query bootstrap 2000 draws (fixed seed 20261101 + dataset index), exact two-sided paired/binomial tests and Holm across the three primary comparisons. Report wins, losses, denominators, absolute coverage, original-judged-relevant coverage, resource skips and every failure. Do not infer real-noise semantic preservation or Q1 acceptance from significance. If gains fail to replicate, preserve that result and revise the research verdict honestly.
