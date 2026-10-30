# Finite-edit possible-result pools: prospective application experiment

Status: application-driven candidate, not an established novel algorithm or Q1-ready paper. This protocol is fixed before inspecting any retrieval outcomes on either new corpus. Prior experiments and their viewed results are disclosed in the root repository. All results, including failures, remain in the archive.

## Target and application

For fixed stored integer ngram-BM25 weights, a corpus, query q, finite edit lattice L(q,B) and k, return P containing every document that can enter top-k for any q' in L. Include all documents tied at the kth score. Such a pool can be reused to reproduce the full-corpus sparse ranker's top-k during subsequent allowed edits. It is NOT a certificate for arbitrary future typos, semantic relevance, RAG answer correctness or an unrelated reranker. Corpus/scorer/channel/budget/base query changes invalidate the certificate.

This differs from the older reference-retention property. The possible-top-k union itself, regional dominance, interval pruning, partitioning and safe fallback already appear in uncertain top-k and interactive fuzzy retrieval. We investigate the usefulness of an auditable specialization to discrete budgeted text edits; global algorithmic novelty is not assumed.

## Fixed data and model

- Full ArguAna corpus (8,674 documents), full SciDocs corpus (25,657), pinned in sources.json. Neither collection was used in earlier project experiments. No qrels are downloaded or used and no new human/LLM labels are created.
- 64 query IDs per corpus selected by SHA256(pool-v1|dataset|queryId), no score/length filtering. Exact IDs frozen in selection.json. No development/confirmation pooling with earlier rounds.
- NFC, Unicode lowercase, whitespace; first16 normalized tokens, with truncation explicitly reported. Character grams3/4/5 within space-delimited tokens. BM25 k1=1.2,b=.75, weights rounded to integers at scale10^6. Stored integers define the actual scorer; this Python implementation has its own version/hash and does not claim bit-identical logarithms to the browser or older float ranker.
- Compact channel: unchanged plus at most one deterministic deletion, adjacent swap, QWERTY-neighbor replacement per token. For each operation family choose by SHA256(token|operation|variant), never by model score or labels. B=1,2; k=5,10. This finite compact channel is deliberately enumerable; NOT all keyboard errors or a natural typo distribution.
- Every selected query, including OOV/zero-score/tied/identity cases, is retained. This is a derived finite-edit oracle audit collection over inherited real text, not a new natural-language dataset.

## Comparators and candidate

1. Whole-corpus exact enumeration with cached integer token scores and incremental score updates; computational ground truth, include all boundary ties.
2. Root independent, budget-aware score envelopes and kth lower-bound threshold.
3. Budget-aware persistent-anchor dominance: clean top max(20,2k) anchors, retain a document unless k anchors provably strictly outrank it for every shared edited query. Anchor restriction affects tightness only, not soundness; all corpus documents remain covered by interval or dominance checks.
4. Matched two-token partition using first two positions as an ablation.
5. Candidate: initial coupled pool intersected with the union of conditional interval pools over every assignment of the two tokens with largest score ranges. This is a finite-state specialization of established partition/dominance ideas, NOT an implementation of UTK's original RSA/JAA and NOT claimed to beat those unimplemented algorithms.

Every split assignment respecting the shared edit budget is covered, including raw states. Depth0 is the root safe fallback; no random sample certifies a pool. Exact minimal union is only claimed for complete enumeration.

## Outcomes and validation

Primary correctness: zero missing oracle documents for every method/query/B/k; statewise cached/full top-k agreement follows from containment and fixed scores, and is checked directly by an independent verifier. Primary utility: per-query proposed pool size/slack relative to coupled root and exact union. Report both improvement and equality/worsening versus fixed partition; no post-hoc best-channel selection. Report corpora separately and descriptive statistics, with no IID p-value over dependent B/k replicas.

Run three balanced-order timed repetitions of the entire candidate-pool construction (shared factors separate). No concurrent numerical experiments. Measure direct full-corpus sparse query scoring versus cached scoring for 20 hash-ordered admissible query states per query. Include initial factor scoring and certificate construction in cache initialization. Report observed per-query break-even number of edits; when cache per-edit cost is not lower, or break-even exceeds measured sequence length, say so. This is local single-machine microbenchmark evidence, not production web latency or measured user behavior. Dense cached-factor scoring is separately labelled and is not compared to sparse retrieval as if identical implementations.

Persist all token operations, scorer hashes, integer factor matrices, exact per-state top-k outputs, all method pools, split traces, query truncation, source hashes, timings, exceptions and machine/software metadata. A verifier independently enumerates choices in another order, recomputes every state score from the stored integers, verifies each complete top-k trace, containment, and every split's coverage. Factor-vs-original-query re-encoding is checked by the runner for all states, not only witnesses. Model index rebuild and full-source replay are separate commands requiring public downloads.

Correctness testing covers random finite factors, conditional envelope soundness, zero scores, ties, repeated tokens, Unicode, full-query re-encoding and stale certificate invalidation in the web integration. Passing tests or positive application results do not establish global novelty or Q1 acceptance. An independent closest-method/mathematical review and broader natural-query evaluation remain necessary.
