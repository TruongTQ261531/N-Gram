# Prospective full-query experiment on a separate research branch

Branch research/rank-equivalence-2026-10-30; parent main94a9f0c16ab2bd312621682cb842fb9b439deabe. Do not merge or push to main, and do not publish changes to the existing live Site. The original archives and their metrics remain unchanged.

## Hypotheses and limits

Earlier reusable pools were conservative, expensive to initialize and tested with first16token truncation. Test (a) compiling budgeted interval bounds once, giving exactly the same conservative pool with less repeated work; (b) exact possible-top10 unions after that certified projection; (c) merging token edits with identical ranking effects, keeping minimum cost and token multiplicity. These are implementations/specializations of known bounds, equivalence and symmetry ideas. We do NOT assume sufficient method novelty for Q1. Preliminary inspection of old16token data found little per-position score compression. Four already-viewed records and timings are separately retained in development.json; they are not fresh confirmation.

## Inputs fixed before new outcomes

-16 new ArguAna and16 new SciDocs query IDs, selected by SHA256(exact-pool-v1|dataset|id). Exact IDs and query source hashes in selection.json. Exclude every previously evaluated ID and identical normalized full query; additionally exclude ArguAna topic families previously used. SciDocs has no equivalent family metadata; corpora remain the same, not new domains.
-Use COMPLETE normalized queries without token truncation. Selected lengths351/143/... and4/14/... are source metadata only. Retain every selected query, including ties, all-zero states and resource-limited cases.
-Same full corpora8674/25657 and pinned original integer rankers as pool_study. Verify downloaded-byte hashes and canonical integer-index hashes before running. Same deterministic compact edit channel; no natural typo distribution or semantic-equivalence assertion. No qrels/new human/LLM labels; no new model fits.
-Primary target B2,k10 with all kth-score ties. No post-hoc favorable B/k selection. Arithmetic int64 under stated conservative range guard.

## Methods

1. Existing scalar partitioned approximation, unchanged parent core, excluding its fixed-split ablation from measured construction.
2. Compiled approximation: precompute raw scores and largest B+depth gains/losses per document; exclude fixed token IDs and use remaining budget. Same two split positions and complete conditional assignments. Must return IDENTICAL pool to1 for every record.
3. Exact enumeration on the compiled certified pool without merging states, batched incremental changed-token deltas. This isolates projection/vectorization from quotienting.
4. Per-position exact-score-effect merging, no position merging.
5. Repeated-text token-type grouping with multiplicity, a matched symmetry control.
6. Candidate rank-effect merging: project onto the safe pool; quotient form deltas modulo a common score shift; drop raw-equivalent options at minimum cost0; group positions with identical effect sets and retain multiplicity. Enumerate every permitted multiset of up to2 nonzero effects. Export representatives and every quotient-state top-k bitset.
7. Full-corpus batched exact enumeration when original state count times corpus size<=100million, retained as resource_unknown otherwise. A skipped full oracle is not a failure or a certified attack. No claimed comparison with unimplemented original UTK RSA/JAA.

Exact modes have a2million-state/500million projected-cell cap. On exhaustion return the safe compiled approximation and explicit resource_unknown. Never call it an exact minimum. Quotient merging can be useless; report equality and any slower runs as well as compression. State counts are logical combinations, not independent user queries.

All exact comparators use the same standard closure: if attained top-k outputs already contain EVERY member of the safe projected pool, its minimal union is known exactly and enumeration can stop. Check this on the raw state before applying enumeration limits, then after batches. Report theoretical states, actually visited states, termination and enumerationComplete separately; a saturated pool does NOT mean every state was enumerated. Retain all visited descriptors/bitsets and attaining witnesses. This closure is established bound/witness reasoning, not an exclusive new contribution.

## Measurements

Construct legacy/compiled pools three times in alternating order; compare equality each time. Construct exact modes three times in cyclic balanced order. Shared factor construction is separately measured. Save every repeat, time, state count, pool, source hash, proof and exception; do not infer universal superiority from medians.

Also MEASURE actual complete20-edit request sequences, three repeats in cyclic balanced method order: ordinary full-corpus sparse retrieval; legacy initialization+cache; compiled initialization+cache; compiled+rank-quotient exact initialization+cache. Cache paths rebuild token factors and certificates inside each timed session, create a subset index using ORIGINAL stored weights, then process the same20 admissible queries. Include initialization rather than project break-even from components. Query sequence is fixed by hash-ordering deterministic quotient representative descriptors; if fewer than20 exist, cycle and disclose. Each returned set must equal ordinary full-corpus output. This is a controlled synthetic sequence, not observed human behavior; timing does not include loading the shared corpus index. No other benchmark/browser work runs concurrently.

## Independent verification

Independently reconstruct all stored full-corpus token/form scores from original stored index postings using own gram extraction and Python integer accumulation. Rebuild conditional lower/upper bounds without compiled top-list reuse; verify every root exclusion/anchor/split and projection coverage. Check all quotient effects, representative costs, group position multiplicities and coverage of ALL original token options, including raw-equivalent min-cost classes. Independently enumerate original per-position states on the certified projected pool and compare the exact union; verify all saved quotient-state bitsets and replay every attaining witness against the full corpus. This distinguishes symbolic safe exclusion from brute-forcing all full-corpus scores, which may exceed the declared oracle cap.

No p-values treating B/k/timing repeats as independent observations. Report corpora separately, all32 queries, full-query lengths, caps and failure details. Broad algorithmic novelty, natural-query generalization, production latency and Q1 readiness remain separate unresolved claims.
