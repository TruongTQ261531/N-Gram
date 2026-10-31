# Bounded native UTK adapter pilot — 1 November 2026, Asia/Saigon

Scope requested: only the first Argon proposal. Retrospective extension of
cb4532814ddac5fc4f06e22f6a742a789c9899c9; no earlier evidence is replaced.
This is a native NLP **segment** comparison, not the entire correlated lattice.

## Selection and limits, fixed before pilot outcomes

Use all 128 locked WANDS confirmation IDs, unchanged integer scorer, B=2, k=10,
full queries and corpus. Enumerate admissible state descriptors; retain the raw
state and the nonraw state minimizing SHA256(utk-segment-v1|queryId|JSON(state)).
The endpoints are actual complete query states, with no token/dimension projection.
Their segment is contained in the full score-space convex hull. It can expose
relaxation slack but cannot estimate the full convex-hull union or its runtime.

Measure one native RSA and one guard-corrected JAA execution per query, each
with a 1-second subprocess wall deadline and 2-GiB address-space limit; kill
the whole process group at deadline. Process launch, input parsing and R-tree
construction are included; shared input preparation is measured separately.
Alternate method order by query hash, one numerical thread, sequential runs.
No timing significance test or comparison with old measurements on other hosts.
No source, binary or paper with redistribution restrictions is published.

## Exact geometry and numerical contract

For whole-corpus endpoint integer scores A and B, construct U=3B-A, V=3A-B.
A global common shift and power-of-two scale make both coordinates nonnegative.
Export points (U,V,V), w1 in [1/4,3/4], w2 in [1/20,1/10], w3=1-w1-w2.
At the endpoints the ranking is A and B. The sum is independent of w2, so
the entire continuous region represents exactly the score segment.

Use a fixed 24-bit dyadic grid for exported coordinates, exactly representable
by float32. Check the endpoint/full-segment unions against an independent
integer/rational oracle on BOTH original scores and exported coordinates.
Quantization discrepancies are retained, not transferred silently to the
original integer scorer. The oracle includes all kth-score ties; the native
floating implementation is tested against that convention, not assumed exact.

Before native execution, safe projection uses max(Aj,Bj) and the kth largest
min(Aj,Bj), separately for original and quantized scores, retaining the union
of both projected sets. This is safe over the entire segment, not just the
finite endpoints. Store projected scores and exclusion receipts; replay from
pinned raw inputs is required to revalidate original corpus exclusion.

For each focal record, sort exact rational crossing times with other records;
at a simultaneous crossing remove departing strict superiors before testing,
then add entering ones. Membership is possible iff fewer than k strict
superiors occur at an endpoint or crossing. Store attaining rational weights.
Native reported missing/extra IDs are relative to the exported-score oracle;
never call native output exact merely because it exits successfully.
The rational oracle is capped at four million projected record pairs per
query (except endpoint saturation); capped cases are retained as unknown and
not run natively. This cap is set before any pilot outcomes.

## Reporting

Retain all 128 selected IDs, completed/wrong/timeout/error outcomes, endpoint
ties, quantization changes, preparation/runtime and source/binary hashes.
Continuous extras certified by the oracle are witnesses of relaxation slack
on these segments; they are not new relevance labels or semantic errors.
Neither universal slowdown, SOTA, novel UTK theory nor Q1 acceptance is assumed.
