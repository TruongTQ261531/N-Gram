# Integer-safe projection before factor materialization

Let x[i,a,g] be the nonnegative integer n-gram count of form a at original
token position i, and let W[g,j] be the unchanged nonnegative integer index.
The same form vector a scores every document. At most B positions change.

For each feature, define h[i,g] = max_a x[i,a,g] - x[i,0,g], which is
nonnegative because raw is an available alternative. Set

`u[g] = sum_i x[i,0,g] + sum of the B largest h[i,g]`.

For every allowed state, its feature count is at most u[g]. Therefore
`H[j] = sum_g u[g] W[g,j]` bounds its document score. Choices that maximize
different features need not agree; this makes the bound loose, not unsafe.
Repeated token types can contribute several copies of the same gain only
up to their actual original-position multiplicity.

Choose at least k anchor documents without looking at query outcomes. For
each anchor j, compute the exact token-budget minimum by subtracting the B
largest raw-minus-minimum-form losses from its raw score. Let L[j] be that
minimum and tau the kth largest anchor L. For any allowed state at least k
distinct anchors have score at least tau. Thus a document with H[j] < tau
cannot be in tie-inclusive top-k. Equality MUST be retained.

Consequently `P = {j: H[j] >= tau}` contains the union of every permitted
top-k result. Computing factors only on P, with the original index weights,
preserves all top-k sets and ties. Any later sound refinement or complete
rank-effect quotient may operate on that projection. An incomplete exact
refinement must return a safe superset/UNKNOWN rather than falsely label a
minimum pool exact.

The implementation checks an integer range bound before multiplication.
Sparse full-query re-encoding, independent state enumeration and original
integer index rebuilding provide separate numerical checks. Neither a hash
nor these checks are a formal proof of all Python/NumPy/SciPy machine code.

## Originality boundary

This envelope/anchor construction specializes established safe screening,
threshold and uncertain-top-k arguments. Round3 already supplies related
feature-space screening for reference retention. Copying that principle
into a pool pipeline is NOT presumed novel. The present stage establishes
whether it removes the practical factor-materialization bottleneck and
provides an independently testable prerequisite for further adaptive work.
It must not be renamed into a claimed new theorem merely because timings
improve. UTK, threshold algorithms, discrete verification and equivalence
reduction remain required closest-method comparisons.
