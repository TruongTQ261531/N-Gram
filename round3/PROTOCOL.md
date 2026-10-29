# Superseded development protocol: strict set invariance

Historical screen only. The 20 SciFact and 20 NFCorpus development cases were completed; no confirmation scores were run under this property. This protocol was superseded BEFORE confirmation by PROTOCOL_RETENTION.md. Preserve the zero nontrivial top-10 invariance outcome, not as a claimed failure/success of the later retention property.

Status: candidate study, not verified new or Q1-ready. No new human annotation.

## Why this scope

CAPC did not establish its ambiguity-weight mechanism; BOLT did not establish contextual/exact-training benefits over strong controls. Do not presume their hybrid helps. Investigate an inference algorithm instead: certify strict top-k set dominance when ALL documents receive the SAME perturbed query. Separate document score intervals discard this shared decision and can be loose.

The ordinary sparse-retrieval scorer is fixed; this candidate does not claim to improve its ranking relevance scores. The contribution hypothesis concerns exactness/tightness, attaining attacks, whole-corpus coverage and efficiency. Generic max-margin verification, top-k certification, BM25, safe pruning and budgeted optimization are prior art.

## Data and fixed choices

Pinned BEIR SciFact (5183 documents), NFCorpus (3633), FiQA (57638); source revision/byte hashes in download_manifest.json. Corpus and qrels stay local. Use all corpus documents with title+text, no hidden top-100 candidate cutoff. Vocabulary/IDF fit indexed documents only, not query labels. Corpora are retrieval collections, not classification test leakage.

Character n-grams 3/4/5 within whitespace tokens with space boundaries; BM25 k1=1.2, b=.75. Word BM25 is a relevance baseline. No parameter tuning. All methods receive the first 32 normalized whitespace query tokens; record truncation and do not claim full-query BEIR SOTA.

Screen: 20 query IDs from official dev (NFCorpus/FiQA), train (SciFact). Confirmation: 100 official test query IDs per dataset. Fixed selection is SHA256(dataset|phase|query-id), independent of performance. Selection IDs, code/configuration hashes must be frozen before any confirmation metrics. Source-file schema/count audits may read files, but no test metrics guide the method. Previously viewed Vietnamese test sets are not used.

## Threat model and property

Each original query token is unchanged or receives ONE deletion, adjacent transposition, repeated-character insertion or QWERTY-neighbor substitution. Include ALL such variants, deduplicated. At most B original tokens change, B=0/1/2/3. This is not all strings in a Levenshtein ball; no whitespace change, unrestricted insertion, synonym or semantic-preservation claim.

K=1/5/10. Certify that every clean top-K member strictly outscores every outsider for every allowed query. Ties and floating ambiguity are not certified. Ranking relevance and prediction invariance are separate. A failed stability certificate does not automatically imply lower nDCG or changed meaning.

## Comparators and runs

1. Independent per-document, budget-aware score intervals (safe but potentially loose).
2. Full coupled exact pair oracle over all corpus outsiders and top-K insiders.
3. Coupled oracle with safe independent-bound screening. Same certificate profile expected, fewer pair evaluations; screened margins are upper bounds, not exact global maxima.
4. Random perturbations: 3 fixed seeds, 10 samples per seed/budget, diagnostic attacks ONLY, never a certifier.
5. Word and character BM25 clean nDCG@10/Recall@10/Hit@1 for relevance context, not direct substitutes for certifier comparisons.

All certifiers use the identical ranker. Exactness in real arithmetic: per token select the alternative maximizing the competitor-minus-insider score gain, then choose up to B largest positive token gains. This is established budgeted linear-separation machinery; novelty is not asserted from this formula alone.

Floating form-score intervals use the conventional nonnegative-dot-product forward-error bound, conservative gamma, and nextafter for outward propagation. The target real-valued scorer uses the stored float64 index weights. Document machine-arithmetic assumptions; numerical testing is not a formal machine-code proof.

Compute full/pruned methods in deterministic balanced order; include shared alternative scoring in end-to-end times, also report post-scoring times, all queries and robust/vulnerable strata. Query labels affect relevance metrics only. Do not claim speed superiority if measured total time does not improve. Index/build cost and memory recorded separately. At most two numerical CPU jobs concurrently under 2-core/8-GiB limits; do not rank methods by concurrent wall-clock training time.

## Checks and decision

Toy exhaustive differential tests; direct re-encoding of real witness queries and full-corpus reranking; independent MILP pair comparisons; interval coverage checks; full/pruned agreement; no random attack may violate a positive certificate. Save every query ID, certificate, upper margin, top-document IDs, witness operations, times and failures. Three seeds are sampled-noise repeats, not independent fitted models or independent datasets.

Use paired query bootstrap for uncertainty, conditional on fixed corpora/models/selected query subsets. No multiple-comparison-adjusted universal superiority claim. A Q1 contribution is NOT inferred from a numeric gate. Proceed from screen to confirmation only if exactness checks pass and there is a practical tightness/efficiency gain worth investigating; preserve negative results. Even positive confirmation still requires closest-method comparisons, broader novelty verification and a suitable journal submission.
