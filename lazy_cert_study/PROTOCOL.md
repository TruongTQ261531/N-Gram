# Lazy finite-edit certification: development and prospective confirmation

Prepared 31 October 2026, Asia/Saigon; base commit 2b2611f.

## Scope and hypotheses

The current exact-pool pipeline materializes token-form scores against the
entire corpus before safe projection. This experiment first tests whether a
feature-space bound and anchor lower bounds can project safely before dense
materialization. This screening is an engineering specialization with close
precedents in round3/screening.py and threshold/uncertain-top-k methods; it is
NOT presumed to be a new algorithm or a Q1 contribution.

H1: the index-first pipeline preserves every possible tie-inclusive top-k
result and returns the same exact union whenever exhaustive refinement
finishes. H2: avoiding full-corpus factor materialization reduces end-to-end
certificate time, not merely an isolated kernel. H3: an online application
must outperform ordinary memoization AND incremental sparse delta scoring,
including initialization, before an online-speed claim is supported.

The implemented target is the parent's stored integer scorer and declared
compact token edits, with an upper bound on changed original tokens. Natural
typo coverage, relevance improvement and unrestricted Levenshtein robustness
are not measured. No human or LLM relevance labels are created.

## Development versus confirmation

Official WANDS inputs are pinned in sources.json. Index all 42,994 products;
the representation and model hash are recorded in the index receipt. Select
480 query IDs by SHA256(lazy-cert-wands-v1|query_id): first64 development,
next128 prospective confirmation, remaining288 reserved unseen. selection.json
was written before any of these retrieval outcomes. Only development queries
may guide implementation choices. Existing product-relevance labels never
guide these choices. There are no new labels by humans or LLMs.

All 32 exact_pool_study queries and the earlier pool/retention queries are
already observed and may be used for engineering development ONLY. Synthetic
corpora may test correctness, never substitute for corpus confirmation.
New confirmation query IDs and source byte hashes must be frozen before
their retrieval outcomes, after development choices are fixed. A later
method/protocol change requires a disclosed amendment and a new confirmation
sample, not retrospective rewriting. No old evidence is overwritten.

Public-source access is currently restricted. A separate environment draft
requests scholarly and Hugging Face destinations. Saving that draft alone
does not apply networking, download data, or validate a method.

## Required controls and measurements

- Parent full-factor compiled projection and exact rank-effect quotient.
- Full-query batched exhaustive enumeration, and the same ordinary batching
  after the feature screen. A standard sparse feature-row extraction is
  shared by all projected methods; this optimization is not a new mechanism.
- Feature-bound screening alone, followed by exact projection refinement.
- Ordinary full sparse scoring, exact-query memoization, and incremental
  scoring of changed token n-grams with full-corpus top-k selection.
- All methods use the same unchanged index, forms, tie convention and
  request sequences. No baseline is denied a standard cache or closure.
- Record feature construction, sparse scoring, projection, factor
  materialization, refinement, request times, peak memory and work counts.
- Measure actual 1/5/20-request distinct and repeated sessions, with startup
  included; rotate execution order, run sequentially and report raw repeats.
  A timing repeat is not an independent query/user.
- Resource limits produce an explicit safe superset or UNKNOWN, not a false
  exactness claim. Retain zero-gain, OOV, zero-score and all-tie cases.

Budget B=2 changed original token positions; k=10. Include all boundary ties.
Use compact_forms unchanged from pool_study, not all character edits. Warm
the immutable index equally for every method; separately report index build
cost. A 20-request sequence attempts raw +6one-edit +13two-edit distinct
texts; if the lattice has too few distinct strings, cycle those available
and report the actual unique count. The repeated scenario repeats its first
10 requests. These are synthetic sequences, not observed user behavior.
All methods may memoize exact requests and use the all-zero witness shortcut.
Rotate method order by query/repeat, three repeats for confirmation. No other
study benchmark runs concurrently. Independent recursive full-query oracle
cap: 50,000,000 state-document cells. Unknowns stay in denominators; no
cherry-picking only cases where the candidate finishes. Each oracle request
uses original full-index scoring; all serving outputs must match exactly.

Choose one candidate using development only, then freeze source hashes,
selection, analysis and choice in confirmation_freeze.json and a Git commit
before running any confirmation query. Primary comparisons are (a) total
certificate time versus the faster per-query control of parent and batched
enumeration, and (b) 20-request startup-inclusive distinct-scenario time
versus the faster per-query memo/incremental control. This oracle choice of
control is deliberately stronger than a fixed deployable baseline. Aggregate
repeats by median per query, using all queries. Report geometric speed ratio,
paired query bootstrap percentile95%CI (20,000 draws, seed20261031), win/tie
counts and one-sided paired sign test with Holm over the two primary tests.
Engineering gate: geometric speed ratio>=1.2, bootstrap lower>1 and Holm
p<.05, with zero oracle/output mismatches. A failed gate is a NO-GO for that
claim, not a reason to swap the primary metric. Prefix1/5 and repeated-session
results are descriptive. No numerical gate certifies novelty or Q1 readiness.

The serving microenvironment receives already-admissible requests from the
driver. Parsing a new user request, scope-membership checking, network time,
browser storage, fallback/rebuild and a concurrent production load are not
measured. Do not call these measurements production end-to-end latency.
Peak VmHWM is process-wide, not a separate per-method memory measurement.
One domain and synthetic sessions support only a bounded engineering claim.

Descriptive relevance context: clean-query nDCG@10 with existing WANDS grades
Exact=2, Partial=1, Irrelevant=0; exponential gain2^grade-1, unjudged0. Break
ranking ties deterministically by the source index's lexicographic document
IDs for this metric only; certificate pools retain ALL boundary ties.
Report top10judgment coverage. Every certifier uses the same clean ranking;
these measurements cannot establish relevance improvement.
Input integrity inspection found 1,467 repeated query-product pairs, 14 with
discordant grades. Collapse repeated pairs by the maximum existing grade,
without changing source bytes; report this policy and counts. This amendment
was made after an integrity assertion stopped the first quality run, before
any relevance metric or confirmation outcome was computed.

## Gates and originality

Zero oracle mismatches are required. A time advantage against a deliberately
unoptimized baseline is insufficient. If ordinary incremental scoring wins,
do not claim online speedup. Positive timings alone do not establish novelty.
The final report must distinguish a useful engineering prerequisite from a
defensible new method, and compare the exact equations with UTK, threshold
algorithms and finite-state/symmetry reduction. Independent mathematical and
closest-method review remain necessary before a submission-readiness claim.
