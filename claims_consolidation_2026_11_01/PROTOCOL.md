# Claim consolidation and all-query replay — 1 November 2026 (Asia/Saigon)

Base: origin/main b4b167194abad0e3a6fb0522b9a141dcb75674d4, containing8538849.
User scope: consolidate CURRENT claims; no new algorithm, channel, model,
dataset or novelty-development experiment. Paper files remain outside Git;
Fig1/Fig2 remain placeholders, no artwork. Keep every earlier scientific freeze.

## Existing refinement, all970 queries

Use ALL original B2/K10 replication IDs: SciFact199,NFCorpus223,FiQA548,
unchanged raw input hashes,index fingerprints,NFC/casefold normalization,
32-token scope and full token-variant channel. No outcome-based selection.
Freeze the IDs and current source hashes before any new measurements.

Run one integrated pipeline on each query: (1) unchanged context/screening;
(2) unchanged default Discrete kernel (40LPcuts,120pairchecks,80candidate
graph cap,existing enumeration); (3) existing pairwise_refine ONLY as routed
by its current bound/candidate count. Its existing settings remain B2,K10,
max80candidates,120seconds additional pair-proof construction. Already-certified
and candidate-cap cases retain their existing bound. A zero-witness context
is explicitly skipped with its full-corpus worst-tie rank; do not pass an
absent margin matrix as a fictitious empty-candidate certificate.

The runner NEVER reads ROBUST/NONROBUST labels or prior successful IDs. Those
files are opened only by the subsequent analyzer/checker. Query IDs and hashes
identify fixed inputs, not outcome labels. Keep every selected query, all caps,
unknown/inconclusive bounds, failures and numerical differences. Do not call
an inconclusive result an attack. Never overwrite old records.

Measure context+default prefix, incremental refinement and their actual total
separately, including per-query preprocessing, excluding shared warm-index
loading. The refined pipeline reuses its own prefix; these are integrated
component timings, not two independently randomized method runs. One numerical
thread, datasets sequential, no simultaneous benchmark. Record host/packages,
all route statuses,pair attempts,certificate groups and all-query/routed latency
distributions. No speedup significance test or GPU/production extrapolation.

After completion, join all970 binary labels from the existing decision archive
to report certified counts, false certifications, monotonicity, baseline replay
differences and costs on robust AND nonrobust cases. The dataset is already
known: this is a RETROSPECTIVE all-query validation, not an unseen confirmation.
Do not retroactively replace original259/260coverage or primary significance.

## Closest-work and manuscript tasks

Inspect primary source content for CostCert,UTK and relevant convex/discrete
verification and fuzzy-pruning work. Record actual source/version/hash/section,
distinguish mathematical mapping from executed baselines, and preserve unresolved
equivalence/priority issues. A bounded review does not prove absence of prior art.
Do not turn standard LP,MILP,Pareto,DSATUR or a corpus reuse into a firstness claim.

Unify the manuscript around one question: which fixed lexical retrieval outputs
can be certified under one shared finite query-edit budget? Reference retention
and possible-result union are complementary contracts with distinct tie rules.
Scorer/channel instantiations remain explicit. Natural-correction and neural
experiments assess assumptions and transfer boundaries; they are not independent
method contributions or sequential components of a measured end-to-end system.

Move lengthy diagnostics/history/source-recovery details to appendices while
retaining their tables/proofs/results. Keep material adverse results visible in
the main text: MILP tradeoffs,failed session gate,scope-limited error coverage,
neural top10(P) loss and standard-depth reranking controls. Revise abstract,
introduction,contribution list,roadmap,section transitions,limitations and
conclusion consistently. No Q1/global-SOTA or global-neural certification claim.
