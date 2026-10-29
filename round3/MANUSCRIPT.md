# Discrete Shared-Query Certificates for Character n-Gram Retrieval

Research manuscript draft, 29 October 2026. Authors/affiliations and target journal have not been assigned. This document has not been submitted or peer reviewed. Originality and Q1 suitability remain unconfirmed.

## Abstract

An unchanged lexical ranker can be stable under many input variants even when independent pairwise bounds cannot certify its output. We study retention of the clean winner within top-K when one shared, discretely edited query scores an entire corpus. For a fixed character-n-gram BM25 index, we combine safe corpus-wide screening, an affine shared-query relaxation and discrete incompatibility covers. Pairwise exclusions use a support test or capped Pareto dynamic programming; resource exhaustion weakens the bound rather than authorizing a certificate. A generic additive-factor construction separates discrete covers from the matched convex relaxation. Experiments use full SciFact, NFCorpus and FiQA corpora, an initial 300-query confirmation and a separately preregistered 970-query replication. Exact pairwise bounds, feasible enumeration, generic LP and time-limited MILP provide matched controls. We release frozen protocols, per-query bounds, numerical witnesses, 27,000 individual sampled predictions and statistical verifiers. The certificate concerns a finite text-edit model and conservative tie ranking; it does not improve the underlying relevance ranker or establish semantic preservation. Results and statistical limitations are reported by stage.

## 1. Motivation and related work

Top-K certification, common-input robustness and relaxed safety properties are established. CertDR and RobustMask certify neural document-ranking defenses, while randomized-smoothing work derives top-K classifier guarantees. CostCert explicitly identifies the inflation caused by independent pairwise use of a shared attacker budget. We therefore make no novelty claim for that motivation or for top-K containment. Our setting fixes an additive lexical scorer and asks how tightly one can bound a target document's rank over finite shared query states without smoothing or fitting a new model.

Current work also includes calibrated candidate pruning, exact geometric exclusion with rounding certificates, conformal multimodal retrieval decisions and domain contamination control. These have different guarantees and assumptions; their published percentages are not compatible baselines for our threat model. N-gram generative retrieval diagnostics and personalized-query benchmarks motivate practical robustness, but our experiments do not certify generation quality or semantic equivalence. See RELATED_WORK_UPDATE.md and bibliography.bib for sources and inspection depth. The specialization remains subject to a broader conflict-graph/disjunctive-verification prior-art review.

## 2. Problem definition

Let W(d,g) be stored nonnegative float64 BM25 weights, treated as exact real parameters. Normalize text by NFC, casefold and whitespace; retain at most the first 32 query tokens. A token contributes within-token character grams of lengths 3, 4 and 5 with boundary spaces. Every original token i has finite alternatives A_i, with raw state zero. Alternatives consist of all single deletions, adjacent transpositions, repeated-character insertions and QWERTY-neighbor substitutions, deduplicated. The allowed query state a changes at most B original tokens. The SAME a is used to score all documents.

For the clean winner r, define d_j(a)=sum_i[f_i(a_i,j)-f_i(a_i,r)]. Its conservative worst-tie rank is 1+sum_j 1[d_j(a)>=0]. A rank upper bound at most K certifies retention for every allowed state and any deterministic tie-breaking. This property is neither strict invariance of the entire top-K set nor a relevance/semantic claim.

## 3. Certificate construction

First bound each document score using featurewise maximum permitted query counts and nonnegative index weights. Bound the reference score below by an exact token-budget oracle. Discard a competitor only when its upper score is strictly below the reference lower score. This examines the full corpus; there is no hidden candidate cutoff. If an allowed state zeros the reference, nonnegativity makes worst-tie rank N attainable and solver work is unnecessary.

For every remaining competitor, exact pairwise maximization takes the B largest nonnegative token gains relative to the raw state. Remove competitors whose maximum margin is negative. Counting the rest gives a valid pairwise upper bound, but different competitors may require incompatible shared edits.

For valid L_j<0 and 0<=w_j<=1/(-L_j), the inequality 1[d_j>=0]<=1+w_j*d_j gives a count bound m+max_a sum_j w_j*d_j(a). The support maximum uses the same token-budget oracle. A cutting-plane master searches for good feasible weights; its restricted optimum is a LOWER bound on the best relaxation, not the robustness certificate. Every reported bound is re-evaluated through the conservative support oracle. A generic compact primal LP over token-state distributions and expected edit budget solves the equivalent relaxation as a mandatory matched comparator.

Next prove that selected competitor pairs cannot simultaneously have nonnegative margins. A negative midpoint support suffices; otherwise a two-coordinate Pareto DP enumerates nondominated upper margin sums by token and edit cost. Dominated points may be discarded because every continuation preserves coordinatewise dominance. Resource limits return unknown and create no incompatibility edge. Partition all possible competitors into pairwise-incompatible groups. At most one member per group can be promoted, so the number of groups bounds the count. Take the best valid LP, cover and feasible exhaustive-enumeration bound.

**Soundness.** Safe screening retains every potentially promoted competitor; outward margin bounds contain its real score; a verified incompatibility edge rules out simultaneous promotion; each returned clique group contributes at most one. Taking minima of independently valid bounds preserves validity. See THEORY.md for the detailed derivation and numerical assumptions.

**Separation.** A single token has M edited states; state k gives competitor k margin 1 and all others -1/(M-1), while raw margins are -1. At most one competitor is promoted discretely, but the uniform fractional mixture makes every expected margin zero, allowing the LP to count M. A complete discrete cover counts one. Nonnegative additive scores realize these factors after adding a common reference offset. This proves a gap for the general factor family, not a new general LP theorem or a physical realization by every fixed BM25/keyboard collection. General additive worst-count maximization contains budgeted maximum coverage; the concrete implementation is conservative and resource bounded.

## 4. Experimental design

Pinned public BEIR mirrors provide all 5,183/3,633/57,638 corpus documents. No qrels fit the index or guide the certificate. Existing original-query judgments are evaluation context only; no fresh human or LLM labeling is used. Parameters are fixed at k1=1.2, b=.75; K=1/5/10/20/50 and B=1/2/3 are reported for primary confirmation, with K=10 primary.

The original 300 test IDs and predictor source were public at commit 8dd7972 before evaluation. Development selected winner retention after a failed strict-set pilot, which remains archived. Primary B2 gains over best LP+enumeration were +5/+4/+5 points, with insufficient exact paired evidence after the original Holm-18 correction. After observing this, B2/K10 was selected for a NEW independent-query replication, preregistered at 5fcf816. All eligible untouched official test inputs were used, with prior input/text overlap and new duplicates excluded, yielding 199/223/548 queries. We do not pool the two stages to rescue significance. Reusing corpora limits claims to new queries on these fixed indexes.

The matched controls are exact pairwise plus feasible enumeration, the best custom/generic same-formulation LP plus enumeration, and a generic numerical MILP with a one-second solver limit and explicit matrix caps/statuses. All methods share ordinary transpose caching. The candidate uses at most 40 cuts, 120 pair checks, 80 candidates for graph work, 20,000 generated DP points and a 1,000-point frontier. Enumeration is capped at 2,000 states and 2 million state-candidate cells. All skips remain visible and are not equated with attacks. The replication focuses on the selected LP/cover comparison; it does not newly claim MILP/random attacks on all 970 queries.

Use 2,000 paired query bootstrap draws and two-sided exact paired tests. Primary multiplicity is Holm-18; replication primary multiplicity is Holm-3. Confidence intervals condition on each fixed corpus/index/query sample. The statistical family and sample sizes are not changed after looking at replication outcomes.

## 5. Results

Initial confirmation, K=10, counts out of 100:

| Corpus | B | Pair+enum /100 | Best LP+enum /100 | Discrete /100 | MILP+enum /100 |
|---|---|---|---|---|---|
| scifact | 1 | 88 | 88 | 88 | 88 |
| scifact | 2 | 60 | 63 | 68 | 66 |
| scifact | 3 | 39 | 41 | 49 | 45 |
| nfcorpus | 1 | 38 | 38 | 38 | 38 |
| nfcorpus | 2 | 19 | 21 | 25 | 25 |
| nfcorpus | 3 | 16 | 17 | 19 | 20 |
| fiqa | 1 | 58 | 58 | 58 | 58 |
| fiqa | 2 | 13 | 15 | 20 | 20 |
| fiqa | 3 | 3 | 4 | 6 | 7 |

Independent replication, B=2/K=10:

| Corpus | new n | Pair+enum | Best LP+enum | Discrete | Difference pp [95% CI] | p Holm (3) | Win/loss |
|---|---|---|---|---|---|---|---|
| scifact | 199 | 111 (55.78%) | 115 (57.79%) | 123 (61.81%) | +4.02 [+1.51, +7.04] | 0.015625 | 8/0 |
| nfcorpus | 223 | 37 (16.59%) | 41 (18.39%) | 45 (20.18%) | +1.79 [+0.45, +3.59] | 0.125 | 4/0 |
| fiqa | 548 | 67 (12.23%) | 71 (12.96%) | 91 (16.61%) | +3.65 [+2.19, +5.29] | 5.72205e-06 | 20/0 |

The second table reports percentage-point differences with paired percentile intervals and Holm-adjusted exact tests; wins/losses are discordant query counts. 2 of the three independently preregistered dataset comparisons pass Holm-adjusted p<.05; this supports only the specified certificate comparison, not publication readiness.

The candidate does not dominate the generic MILP: in primary NFCorpus and FiQA B3 the MILP certifies one additional query. Finite-cut LP optimization gaps are gaps to that relaxation, not to the true worst rank. A solver timeout is not a nonrobustness witness. At B1 feasible enumeration and strong controls often remove any advantage; these zero-gain configurations are retained.

Relevance-conditioned results:

| Corpus | n | Winner with positive qrel | Certified and positive-qrel | Fraction of all n |
|---|---|---|---|---|
| scifact | 199 | 108 | 83 | 41.71% |
| nfcorpus | 223 | 102 | 31 | 13.90% |
| fiqa | 548 | 101 | 44 | 8.03% |

An uncertified or unjudged-relevant winner must not be conflated with a genuinely irrelevant document. Stability cannot correct a wrong clean result. Existing qrels describe the original intent and do not validate every perturbed string.

Post-hoc mechanism diagnostic:

| Corpus | B | Best LP+enum | Recorded support edges only | Full discrete |
|---|---|---|---|---|
| scifact | 2 | 63 | 66 | 68 |
| scifact | 3 | 41 | 45 | 49 |
| nfcorpus | 2 | 21 | 23 | 25 |
| nfcorpus | 3 | 17 | 18 | 19 |
| fiqa | 2 | 15 | 19 | 20 |
| fiqa | 3 | 4 | 4 | 6 |

The support-edge column reuses exactly the tested pairs from recorded runs and removes Pareto-only edges. It is not an independent support-only scheduling experiment or a new confirmation. Synthetic M=3/4/8 gap examples and exported real-query fixtures are separately identified from retrieval results.

Audit of independent-stage gain queries:

| Corpus | Gain queries | Generic LP success on gains | Positive-qrel gain queries | Generic LP cap skips / all | Zero-score shortcuts / all |
|---|---|---|---|---|---|
| scifact | 8 | 8 | 4 | 1 | 0 |
| nfcorpus | 4 | 4 | 2 | 0 | 11 |
| fiqa | 20 | 20 | 7 | 20 | 0 |

All 32 additional certified queries have successful generic LP runs with nominal objective above the count threshold 10 by at least 1e-6; no gain relies only on a capped LP comparator. These are numerical solver objectives, not formally verified lower bounds. Thirteen gains have positive-qrel winners (4/2/7), so relevance-conditioned benefit is smaller than stability benefit. This is post-hoc descriptive mechanism analysis, with no new p-values. All cap/zero-score cases remain in the full denominator.

## 6. Verification and cost

Eighteen unit tests include 1,200 exhaustive pair-budget checks, 49 eligible enumerated LP cases out of 60 generated cases, 200 Pareto/brute-force comparisons, 25 MILP/brute-force instances and 210 high-precision interval checks. Full-corpus controlled replay matches all 300 primary rank profiles and all 300 budget-two restricted profiles. Every saved support/MIP witness and 27,000 seeded sampled queries is re-encoded. Individual state choices, observed ranks, retrieved IDs and relevance grades permit offline metric recomputation. No observed strict rank exceeds its proposed conservative upper bound. This empirical statement does not replace the mathematical certificate or prove the compiled libraries correct.

Twelve exported real-query margin fixtures support numerical solver audits; eight finite lattices are independently enumerated. Proof traces and resource outcomes are retained per replication query. Checksums, public precommits, uncompressed-result hashes and input-disjointness hashes support provenance. CI verifies the published evidence and numerical components; it does not certify originality or acceptance.

All 20 downloaded source-file byte hashes were rechecked. Rebuilding SciFact character and word indexes directly from raw data, without cache pickles, matches their frozen canonical fingerprints. This is a representation reconstruction for SciFact only, not an independent implementation or a claim of rebuilding all three indexes.

We discovered that the original confirmation initialized OpenBLAS with three threads due to import order, despite a one-thread protocol. The original evidence is preserved and concurrent times are not used for latency claims. Controlled replay initializes BLAS/HiGHS with one thread before imports and profiles sequential fresh corpus workers. First ten fixed queries per corpus receive balanced method order, warmed indexes and end-to-end B1/B2/B3 timing. Median seconds:

| Corpus | Pair+enum | Custom LP+enum | Generic LP+enum | Discrete | MILP+enum |
|---|---|---|---|---|---|
| scifact | 0.437 | 0.462 | 0.515 | 0.547 | 0.825 |
| nfcorpus | 0.188 | 0.246 | 0.261 | 0.246 | 1.559 |
| fiqa | 2.878 | 2.870 | 3.037 | 3.119 | 4.127 |

Startup is reported separately; primary FiQA replay peaks near 3.68 GiB. Ten timed queries with one measured pass per method are limited latency evidence, not a production speed claim. The generic MILP time includes setup/oracle work and may exceed its solver time limit. Concurrent independent-stage times are diagnostics only. Execution-only FiQA partitioning after a retained 57-query prefix is documented and source-identity checked; its fixed ID sequence and per-query computation are unchanged.

## 7. Limitations and submission status

The threat model is a finite QWERTY/token-edit lattice, not all edit-distance strings or semantic rewrites. English corpora, bounded queries, conservative ties and fixed corpus reuse limit generalization. Whole-corpus FiQA is moderate scale; no million-document or online serving result is claimed. The unchanged BM25 ranker can retrieve unjudged or wrong results. Float guarantees assume the stated IEEE-754 and sparse-dot error model; there is no mechanized proof of scipy/BLAS/HiGHS. Resource caps may yield loose but valid bounds.

The contribution is a specialized combination with demonstrated behavior, pending a dedicated closest-method review beyond IR and independent theoretical/code review. CostCert and general disjunctive/conflict-graph verification are particularly relevant novelty risks. New-corpus/language or existing natural-typo evaluation is needed before broad deployment claims. Journal scope and current quartile require primary-source verification. Statistical gains, artifacts and this draft do not establish Q1 readiness or guarantee acceptance.

## Data and code availability

Code, frozen protocols, IDs, compressed per-query records, individual prediction arrays, fixtures, CSVs, plots, execution history and offline verifiers are in this repository. Raw corpus/index/Word files are excluded; pinned upstream data are fetched for full reruns. See DATA_LICENSE.md, REPRODUCE.md, THEORY.md, NOVELTY.md, RELATED_WORK_UPDATE.md and bibliography.bib. No experiment in this round requires a GPU, paid API or new human annotation.
