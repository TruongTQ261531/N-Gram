# Exact scope of a reusable finite-edit pool

Let F[t,a,j] be stored nonnegative integer scores for token position t, admissible form a and document j. Form0 is raw. A query state a has cost sum_t 1[a_t !=0] <= B and score S_j(a)=sum_t F[t,a_t,j]. Define T_k(a)={j:S_j(a)>=kth_largest_i S_i(a)} and U=union_a T_k(a). Boundary ties are included, so a top-k set and its union may contain more than k documents.

The minimum exact reusable pool is U by set inclusion. The candidate returns an upper approximation P, not a minimum. If U is contained in P and the stored scores are reused, computing top-k over P returns exactly T_k(a) for every admissible a. This is a result-set equality statement, not a semantic relevance or RAG-answer statement.

## Interval exclusion

Within a conditional node with some token forms fixed, subtract their nonraw costs from B. Sum the fixed contributions and remaining raw contributions. For each document, add the largest at-most-remaining positive token gains to obtain H_j; subtract the largest token losses to obtain L_j. This gives L_j <= S_j(a) <= H_j for every completion.

Let tau be the kth-largest L_i over the full corpus. If H_j < tau, at least k documents have scores strictly greater than S_j(a) for every completion. Thus j cannot appear in T_k(a). Equality is kept, preserving all ties. No independence of document scores is required for this sufficient exclusion; dropping correlation only loosens the bounds.

## Shared-query anchor exclusion

For an anchor i, compute M_ji=max_a(S_j(a)-S_i(a)). Add the raw margins and the largest at-most-B positive gains across original token positions; the budgeted separable maximum is exact for this finite cost model. If M_ji<0, i always strictly outranks j. A document with k such distinct anchors is safely excluded. Restricting the checked anchors can only enlarge the pool. This is established budgeted linear optimization and persistent dominance, not claimed new mathematics.

## Conditional cover

Choose up to two token positions without using qrels and enumerate ALL admissible assignments at those positions. Each full state has exactly one such assignment. For each node produce a safe conditional interval pool P_v. Intersect the root safe pool with union_v P_v. Since every full state belongs to a covered node, the intersection remains a superset of U. Choice of split affects cost and tightness only. The adaptive heuristic uses largest token score range; the matched ablation uses the first positions. If the browser hits its work cap, it discards incomplete refinement and returns its root safe pool. An incomplete list of branches is never used as a complete certificate.

## Arithmetic and invalidation

Python uses int64 with an a-priori margin/score range guard below INT64_MAX/32; the independent source replay accumulates Python integers. The browser reuses its original score guard below MAX_SAFE_INTEGER/16. The stored rounded weights define each target scorer; no proof of correctly rounded logarithms or compiled runtime is asserted. The Python and browser index builders have distinct version/hash identities.

P depends on the corpus, stored weights, base query, forms, budget and k. A new corpus, recomputed IDF, scorer change, channel/budget change or query outside the lattice requires a new certificate. Browser UI invalidates on setting/input changes, the worker rejects stale hashes/base queries and a finite-state membership matcher rejects out-of-lattice replays. Deleting a one-character token, producing an empty form, is handled explicitly.

This proof is for the mathematical algorithm under the stated integer-range assumptions; exhaustive tests validate recorded instances. It is not a formal proof of all JavaScript/Python/library machine code. The broader uncertain-top-k task, dominance and partition principles substantially overlap UTK and related work listed in RELATED_WORK.md.
