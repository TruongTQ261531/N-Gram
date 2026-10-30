# Application study v0.1 — frozen before audit-set outcomes

30 October 2026. Goal: implement and test a browser-local retention service and a replayable **synthetic/semi-synthetic audit set**, extending the existing ngram research with a practical workflow. This is not a prospective real-user trial, a naturally occurring query dataset, proof of global originality, or a Q1-readiness gate.

## Application object

Use `ngramlab-fixedpoint-v1`, a NEW scorer, distinct from round3's frozen float64 BM25. Normalize by NFC/Unicode lowercase/whitespace; use within-token char grams3/4/5. Compute BM25 k1=1.2,b=.75 then round coefficients to integer scale10^6. The stored integer weights define the certified model. All subsequent query-score, margin, support and Pareto operations are integer additions/subtractions; reject queries when the declared conservative score bound exceeds MAX_SAFE_INTEGER/16. This does not prove logarithm generation exact or formally verify JavaScript/compiled code.

Reference is the raw-query winner, ties broken by document ID. Certified rank uses the WORST tie order: 1+number of other documents scoring >= reference. Fixed full corpus and same perturbed query for all documents. B=1/2 changed ORIGINAL token positions. No semantic/relevance label is inferred.

For a valid upper bound U, returning depth K>=U is sufficient to retain the reference when every allowed perturbed query is reranked with the same corpus/scorer/tie model. U is the smallest depth justified BY THAT BOUND, not necessarily the true minimum. Only exhaustive worst rank R* establishes the minimum sufficient depth. Showing clean top-K now does not guarantee retention of every future winner or all relevant evidence. U>cap without a counterexample is unknown; an observed rank>cap is a concrete counterexample to that cap.

## Algorithm and controls

Exact pairwise maximum margins via top-B token gains; discrete pair conflicts via integer support test/Pareto DP; valid clique partition count upper bound. Caps:120 pair checks,80 candidate documents,20,000 generated points and1,200 frontier. Unknown never creates a conflict edge. Browser production also enumerates when <=5,000 states and <=2million state-document cells. There is NO LP backend in this browser engine, and the published float-scorer LP/MILP results are not reused as measurements of it.

Compare exact pairwise, cover without enumeration, complete deployed pipeline with small-lattice enumeration, and an exhaustive oracle on the SAME integer model. Include the enumeration comparator so gains are not attributed to the discrete graph when brute force already solves the input.

## Fixed inputs and source/license

48 original authored synthetic EN/VI knowledge-base documents,48 authored query seeds,12 source-topic families. Corpus/query files are explicit inputs, not sampled after metrics. No new human relevance labels; source anchors are provenance, not relevance judgments.

English channels:keyboard,curated,mixed. Vietnamese:keyboard,accent omission,mixed. B=1,2 for each:48×3×2=288 planned cases, no quality-based exclusions. Keyboard permits one delete/adjacent swap/repeat/QWERTY-neighbor per original token; accent omission strips marks and maps đ->d as a separate whole-token operation. Mixed is the union of declared alternatives, at most one state per original token. Curated channel reverses single-word unique-correction codespell pairs, filters targets to authored input vocabulary, sorts and retains first8 errors/target. This is a declared FINITE subset, not all spelling errors or frequency sampling. Retain identity lattices where no alternative exists and report them.

codespell revision4ce1caed2f97a50031225545c9697d9ef885c09b; source SHA/license/filtering in `webapp/dist/data/data-license.json`. Dictionary CC BY-SA3.0; synthetic source text CC0. No codespell GPL code is imported. Combined distributed dictionary-derived audit set carries CC BY-SA3.0 notices. Transplanted curated pairs are semi-synthetic errors, never claimed as real user logs.

## Group split and scope of inference

Assign SHA256(family) first8hex modulo5==0 to evaluation, otherwise development. Language counterparts, sibling queries, channels and budgets share the same family split. Do not move cases after seeing results. This controls source-family overlap only; all cases share the fixed corpus and authored subject matter. It is not independent corpus/domain generalization or a claim of linguistic naturalness. Report all cases plus split-specific descriptive results. No significance gate or IID query bootstrap over correlated variants.

## Complete records and independent verification

Freeze engine, generator, oracle verifier, analyzer, protocol and exact inputs before outcome generation; publish their digest to GitHub first. Save corpus/model hashes, all integer weights, token alternatives/operations, factor scores, margins/conflict traces/groups, resource status, observed witness, and all enumerated state choices/ranks.

Gold oracle limit200,000 states /10million cells. Preserve UNKNOWN if exceeded; do not fabricate exact labels or silently trim cases. Recompute all token-document scores independently in Python using the stored integer weights. Independently enumerate choices by combinations/products with arbitrary-precision Python integers; check all saved state ranks, maximum, every successful conflict edge, group partition, and that every bound is sound. Verify family split isolation and no duplicate/missing IDs. These are exact checks of finite recorded instances, not a proof for all future inputs.

## Fixed descriptive analysis

For language/channel/B/split report n, identity lattices, exact-oracle availability, state counts, mean/median worst rank, excess depth above gold for each control, cover improvement counts, production-enumeration use and resource UNKNOWN. At caps1/5/10/20 report certified counts and oracle-feasible but abstained cases. Record observed cap violations. No RAG-generation, relevance, user productivity or latency superiority claim is planned. Concurrent durations are diagnostics only.

The deployment adds corpus import JSON/JSONL/CSV, explicit error channels, counterfactual witness replay, sufficient-depth policy, batch record creation and downloadable self-contained evidence. Browser limits500docs/500,000chars/16tokens, not full FiQA live serving. Do not present routine web features or a small synthetic dataset as automatically Q1-level novelty. Closest prior art and license limits are in RELATED_WORK.md.
