# Whole-corpus retention bounds for finite query edits

These are derivations for this implementation. Support oracles, LP duality, Pareto DP and clique-cover bounds have prior art; a derivation here is not a claim of first discovery.

## Scorer and property

The index stores nonnegative float64 BM25 coefficients W(d,g). Treat these stored numbers as exact real parameters. A query is the sum of character-ngram counts within its normalized whitespace tokens. Each token i has finite variants a in A_i, with raw a=0; at most B tokens use a nonzero variant. Let f_i(a,d) be a token's additive score. The same choice vector a is used for EVERY document.

For the clean winner r define d_j(a)=sum_i[f_i(a_i,j)-f_i(a_i,r)]. The worst-tie rank is 1+sum_j 1[d_j(a)>=0]. This counts every tie ahead of r, so a certified upper rank <=K guarantees retention under any deterministic tie-breaking. It can be conservative when texts duplicate or scores vanish. It does not prove relevance, semantic preservation, or invariance to unspecified edits.

## Exact pairwise oracle

For each token, choose the state maximizing its competitor-minus-reference gain relative to raw. The maximum pair margin is the clean margin plus the B largest nonnegative gains. This follows because there is one unit-cost choice per original token and no cross-token score factors. Minimum margins use the same argument with signs reversed. This formula is standard budgeted linear optimization.

If a document's maximum pair margin is strictly negative it can never outrank r. Counting all remaining documents gives a sound but possibly loose rank upper bound: different documents may need incompatible edits.

## Safe screening before dense scores

For each indexed ngram g, the maximum permitted query count is the raw count plus the B largest token-specific count increases for g. Maximizing each g separately relaxes shared choices. Nonnegative index weights therefore give a document score upper bound by one sparse matrix-vector product. Compute the reference score lower bound by minimizing its token scores jointly under the budget. Any document with upper score < reference lower score can be discarded for this budget. No hidden top-100 cutoff is used.

If an allowed variant gives the reference zero score, all corpus scores are nonnegative, so worst-tie rank N is attained. Structural zero detection is exact for this nonnegative index (positive weights are far above underflow). Returning N is conservative for fixed tie-breaking but exact for the worst-tie convention.

## Shared-query affine-envelope relaxation

For each remaining competitor choose a valid lower margin L_j<0. For any w_j in [0,1/(-L_j)],

    1[d_j>=0] <= 1+w_j*d_j.

For d_j<0 this follows from d_j>=L_j; for d_j>=0 the right side is at least one. Consequently

    worst_count <= m + max_a sum_j w_j*d_j(a).

The support maximization is the same exact token-budget oracle, now for a nonnegative weighted sum of margins. Every feasible w independently supplies an upper bound; a cutting-plane master only tries to improve it. The restricted master objective is a LOWER bound on the best relaxation value, never an upper certificate for true rank.

An equivalent generic primal LP uses distributions over token states, a total expected edit budget <=B and variables 0<=z_j<=1 with z_j<=1+d_j(y)/(-L_j). A compact formulation uses one variable per token-state. The token-budget polytope is the convex hull of the discrete unit-cost choices. Standard LP duality gives the envelope formulation. The optimum relaxation may still exceed the true INTEGER worst count. The reference direct LP is therefore mandatory, not a weak baseline to omit.

The implementation clamps weights to conservative caps and evaluates the support with outward bounds. Thus stopping the optimizer does not invalidate the current upper certificate; it only leaves a looser bound. The reported envelope gap is an optimization diagnostic for this relaxation, not the gap to the true worst rank.

## Discrete incompatibility and covers

Two competitors j,l are incompatible if no allowed discrete query makes both margins nonnegative. A negative upper bound on the support of (d_j+d_l)/2 proves incompatibility. When that fails, a two-dimensional DP retains coordinatewise nondominated partial margin sums for each exact edit cost. A dominated point can be removed because any continuation applied to its dominator remains coordinatewise at least as large. Induction over tokens proves that, if no final upper-bound point has both coordinates nonnegative, no actual query can promote both competitors.

The Pareto frontier can grow exponentially. Resource caps return UNKNOWN/compatible, never a false incompatibility. Missing edges only weaken the result.

Partition all possible competitors into groups whose members are pairwise proven incompatible. Any actual attack can promote at most one member of each group. Therefore the number of groups upper-bounds the simultaneous count. Greedy grouping is not an optimal coloring claim; every returned partition is valid. Take the minimum of this integer bound and the affine-envelope bound. Small lattices are also exhaustively enumerated as a strong comparator and optional tighter bound.

## Why discrete checks can beat the BEST convex relaxation

Diagnostic construction, not a first-known integrality-gap claim: one token has M alternatives. On alternative k, margin d_k=1 and all other margins are -1/(M-1); raw margins are -1. Every discrete query promotes at most one competitor. The uniform fractional mixture of alternatives makes every margin zero, so the convex LP can set all z_j=1 and returns M. Every competitor pair is discretely incompatible; a complete clique cover returns one. Thus the gap between this convex relaxation and a discrete cover can grow with M. Nonnegative score factors realize the construction by adding a common positive reference score. This is a statement about the additive-factor family, not a proved hardness/gap construction for every fixed BM25 corpus or every physical keyboard lattice.

Multiple independent groups give exponentially many query combinations while the cover argument remains compositional. The experimental caps need not recover the optimal cover. Enumeration is explicitly included to avoid attributing a gain on a tiny lattice to a sophisticated algorithm when brute force already solves it.

## Computational difficulty and scope

Worst-count maximization in the general additive-factor family contains maximum coverage: a binary edit for set i contributes one to each covered competitor's margin, with a -1/2 baseline. A budget-B choice promotes precisely the covered items. This explains using conservative bounds rather than claiming polynomial-time exact worst-rank optimization. It does not prove that every concrete BM25 instance is difficult.

## Floating arithmetic

All form scores are nonnegative sparse dot products of integer counts and stored weights. Conventional gamma_n forward-error bounds, with conservative eps and extra operations, enclose the real value. nextafter rounds interval additions/subtractions outward; signed weighted-support dots additionally bound absolute summation error. Pareto DP uses upper vectors, so roundoff can prevent proving an edge but cannot justify an edge from a lower estimate.

Assumptions: finite IEEE-754 float64 arithmetic, standard correctly rounded scalar operations, no unmodelled overflow, and the conventional sparse/BLAS dot-product error model. High-precision checks and independent solvers test this implementation; this is not a formal proof of the compiled machine code or its libraries. MILP is a numerical reference with explicit time limits/statuses, not an unquestioned certificate authority.
