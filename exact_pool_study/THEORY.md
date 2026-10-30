# Safe projection, compiled bounds and exact unions

Target: same stored integer scorer and finite shared-token-edit lattice as the parent pool study, now with complete queries. B2,k10, include all boundary ties. Original corpus/index and allowed token forms stay fixed. This is a candidate specialization of established optimization/equivalence ideas, not an originality certificate.

## 1. Compiling the same conservative bound

For token t/document j define u_tj=max_a F[t,a,j]-F[t,0,j] and d_tj=F[t,0,j]-min_a F[t,a,j]. Both are nonnegative. A conditional node fixes at most d token positions and leaves residual budget r<=B. The original envelopes add the largest r gains/losses among unfixed positions to/subtract from the conditional raw score.

Precompute the largest B+d values and their token IDs per document, separately for u and d. After excluding at most d fixed IDs, every positive gain needed for a top-r sum is present in this list. Sorting the remaining list and taking the largest r therefore returns EXACTLY the original envelope, including ties and zero padding. Here B2,d2, so at most4entries per document suffice. This changes repeated work, not certificate tightness. The implementation must match the old pool exactly on every record; repeated gain caching is not claimed to be new mathematics.

## 2. Project only after a sound whole-corpus exclusion

The parent interval/anchor/complete-partition proof yields P containing every document that may enter top10 under every allowed original state. Reusing original stored weights, top10 with all ties over P equals the full-corpus result for every allowed state. Removing documents based on an ordinary heuristic candidate list would not justify this step. The verifier checks the full-corpus bounds and all split assignments independently.

## 3. Equivalence of rank effects

Let D[t,a]=F[t,a,P]-F[t,0,P]. Choose an anchor coordinate p0 in P and define E[t,a]=D[t,a]-D[t,a,p0]1. Replacing an option by another with the same E changes all document scores in P by one common constant. Ordering and every tie remain identical after adding any other token contributions.

For a fixed position, merge options with identical E. The class containing raw has minimum cost0; other classes cost1. Because the allowed budget is an UPPER bound, taking a minimum-cost representative preserves the reachable set of rankings: every original state maps to a no-more-expensive quotient state, and every quotient state has an actual representative with cost<=B. This would require a different argument for an exact-cost constraint.

## 4. Position multiplicities

Positions with identical sets of available normalized nonzero effects can be grouped. Retain their count and a representative original form for every effect at every position. Choosing two effects from one group is allowed only when it contains at least two original positions; repeated choice of the same effect is allowed in that case. Assignment permutations within the group cannot change the additive score ordering. Every original state maps to one permitted multiset and every such multiset has a valid original-position witness. Context-sensitive or order-sensitive rankers would not permit this grouping without further proof.

If group g has q_g nonzero choices and multiplicity m_g, the number of quotient combinations under B2 is:

`1 + sum_g q_g + sum_{g<h} q_g*q_h + sum_{g:m_g>=2} q_g*(q_g+1)/2`.

This can be much smaller than per-position enumeration when queries repeat token types. Common-shift merging may add no reduction beyond exact-score or text-type grouping. All three controls are measured separately; no gain is automatically attributed to the rank quotient.

## 5. Exact termination by witnessed saturation

Let W be the union of actually evaluated top10 outputs. Always W subset U subset P, where U is the true minimal union. If W=P then W=U=P and further enumeration is unnecessary. Otherwise complete enumeration of the quotient yields U by the equivalence/coverage argument. This standard bound-plus-witness closure is used equally by every exact comparator. Records distinguish theoretical combinations, visited combinations and complete enumeration. A saturated pool is exact without claiming every state was visited.

## 6. Verification and arithmetic limits

Stored integer scores, normalization/form maps, source pins and range guards define the target. The int64 guard leaves conservative headroom for signed deltas, common-shift removal and the two-edit sums. Token/form scores are independently reconstructed using own character extraction and Python integer accumulation. The verifier checks whole-corpus exclusion, all quotient classes/multiplicities/costs, every stored visited state output, and independently enumerates ORIGINAL per-position states over P in another order. It also replays attaining witnesses over the full corpus and verifies session answers.

The guarantee is about retrieval result sets of this exact scorer/channel/budget. It is not semantic relevance, arbitrary natural typos, RAG-answer truth, dynamic-IDF updates or a machine-code proof. The corpus and mathematical target remain fixed. Novelty relative to UTK, automata/verification equivalence and symmetry reduction requires further closest-method review.
