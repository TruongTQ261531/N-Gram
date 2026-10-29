# BOLT: exact oracle and the scope of its guarantee

Let an input have n retained whitespace tokens. Token i has q_i<=3 distinct, same-NFC-length forms z_i in {raw,tone-folded,fully-folded}. c_i(z_i) is the Hamming cost relative to its raw NFC form. Let Z_k = {z : sum_i c_i(z_i)<=k}. Raw state has cost zero, so Z_k is nonempty. Length-changing candidates are omitted rather than silently treated as fixed-length replacements.

The sparse score of class a is

s_a(z) = b_a + (sum_i u_{a,i}(z_i) + sum_{i=2}^n v_{a,i}(z_{i-1},z_i))/sqrt(n).

Canonical token and canonical pair factors are included as state-constant terms. The document denominator sqrt(n) is invariant over Z_k. Token-local TF-IDF normalization is permitted because it is inside u; sentence-global feature normalization or sublinear document term frequency would invalidate this decomposition.

## Proposition 1: exact separation

For intended class y and competitor a, write U_i(s)=(u_{a,i}(s)-u_{y,i}(s))/sqrt(n), and E_i(t,s) similarly for the contextual pair. Define D_i(b,s) as the maximum accumulated competing margin through position i, ending in state s with exactly b cost. Initialize D_1(c_1(s),s)=U_1(s) and all other cells to -infinity. Then

D_i(b,s)=U_i(s)+max_t {D_{i-1}(b-c_i(s),t)+E_i(t,s)}.

The maximum over b<=k and final s, plus b_a-b_y, equals max_{z in Z_k}(s_a(z)-s_y(z)).

Proof: partition all admissible prefixes by their last state and exact cost. Each predecessor prefix is feasible iff it has the displayed predecessor cost; the local decomposition adds exactly one unary and one edge term. Induction on i establishes both upper bound and attainability. Traceback supplies an attaining witness. Time O(n*k*q^2) per competitor and O(n*k*q) traceback storage; value-only memory can be O(k*q). This is standard finite-state/budget dynamic programming specialized to the architecture, NOT a new general DP theorem.

A point is robustly correct on Z_k iff max_z(s_a(z)-s_y(z))<0 for EVERY a!=y. Implementation requires < -1e-9 to avoid certifying near ties. This is a floating-point implementation with extensive differential checks, not a formally machine-verified real-arithmetic solver. All margins, original integer labels and row IDs are saved for auditing.

## Proposition 2: independent-factor upper bound

For any lambda>=0,

max_z margin(z) <= bias + lambda*k + sum_i max_s[U_i(s)-lambda*c_i(s)] + sum_edges max_{t,s}E_i(t,s).

Proof: on any feasible z, lambda*k >= lambda*sum_i c_i(z_i); the factor maxima dominate the chosen unary and edge factors. Taking a minimum over a finite nonnegative lambda grid preserves validity. The bound relaxes shared decisions across adjacent factors; it can be loose. An upper bound below zero is a certificate. Greedy search, in contrast, returns a feasible margin LOWER bound on the maximum, so a negative greedy margin cannot certify robustness.

Example: two binary-state tokens have unary state-1 score -2 each and pair score E(1,1)=10; other scores zero, budget=2. Greedy remains at (0,0) with margin 0, while exact DP obtains 6 at (1,1). This illustrates why contextual interactions defeat independent single-edit gains. It is not itself a novel combinatorial phenomenon.

## Proposition 3: convex robust training objective

For class-balanced weights w_i and alpha>0, eta in [0,1], use

F(W)=alpha/2 ||W||_F^2 + (1-eta)/(N*(C-1)) sum_{i,a!=y_i} w_i [1+s_a(x_i)-s_yi(x_i)]_+^2
 + eta/(N*(C-1)) sum_{i,a!=y_i} w_i [1+max_{z in Z_k(i)}(s_a(z)-s_yi(z))]_+^2.

Each inner margin is a maximum of affine functions of W and hence convex. Squared positive part is convex and nondecreasing on the relevant margin function. The sum is convex and alpha makes it strongly convex. The exact oracle yields violating witnesses for a restricted max-witness objective. Restricted loss is a lower bound on full robust loss. The code reports the full exact-oracle objective minus the restricted objective after every separation call; this is a computable separation gap at the current W, not by itself a global optimality gap unless restricted optimization is also solved to the requisite precision.

The finite L-BFGS/outer iteration caps can stop before optimization convergence. Full logs explicitly retain optimizer success flags, gradient norms and separation gaps. No global optimum is claimed when these diagnostics do not support it. Convex robust optimization, cutting planes and squared hinge are established methods; their use does not prove Q1 novelty.

## Labels and semantics

The certified property is intended-message classification over a fully specified orthographic transmission channel. Existing labels identify the original message; no new semantic annotation is created. We do NOT assert that each resulting visible string has identical literal meaning to every reader. The guarantee excludes arbitrary typos, insertions/deletions, arbitrary synonyms, unseen normalizers, truncation-changing edits, or general Levenshtein balls. Removing accents can cause information loss and irreducible conflicts. Canonical-only models are an essential exactly invariant baseline.
