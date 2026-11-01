# Paper-to-implementation mapping

Primary: Mouratidis and Tang, *Exact Processing of Uncertain Top-k Queries
in Multi-criteria Settings*, PVLDB11(8),866–879,2018,
DOI10.14778/3204028.3204031. Source inspected:
https://www.vldb.org/pvldb/vol11/p866-mouratidis.pdf . The inspected PDF's
SHA256 is recorded with the other primary sources in the prior
claims-consolidation supplement. No third-party source/PDF is redistributed.

This is a **finite-domain adaptation**, not a renamed old batch/parent
control, not native C++ timing and not a claim that every UTK optimization
has been reproduced. The previous native conformance failures are retained;
they do not refute the mathematical algorithms in the paper.

| Paper component | Independent finite implementation | Difference/limit |
|---|---|---|
| Section3.1 linear scores under one uncertain weight | Original integer token-form factors and all one-hot alternative tuples with at mostB2 changed positions | Correlated finite domain, not its convex box/hull; full untruncated WANDS query |
| Section4.1 regional dominance and r-skyband | `minimum_margins`, `regional_filter`: exact full-domain minimum margin; keep fewer-than-k strict dominators | Strict rather than weak dominance preserves all boundary ties; pivot-ordered scan/NumPy blocks replace BBS/R-tree traversal |
| Section4.1 dominance graph | Every survivor stores all its earlier strict regional dominators; pivot ordering makes later strict dominance impossible | Discarded records have k certified surviving strict dominators, with positive exact minima; no inferred edge from an unknown test |
| Section4.2 candidate verification | `rsa_arrangements`: decreasing dominance-count order; candidate-specific state cells with strict-superior counts and rank quota reduced by ancestors | Exact finite state masks replace continuous local cells/LP feasibility; competitor order uses increasing dominance count |
| Section4.2 ancestor propagation | A verified member's strict ancestors receive its same attaining state | No propagation through equal-score records; tie-inclusive witnesses are checked against independent full-corpus replay |
| Section4.3 drill | Exact admissible-state top-k probes; cache only already computed probes within the query | Choose the first still-promising finite state instead of an LP-selected continuous drill vector; no external oracle/labels |
| Section5.1 kth pivot anchor | `jaa_arrangements` picks the kth candidate at a state in the current region | Deterministic ID tie order chooses an anchor only; equality is separately preserved in its output |
| Section5.2/Algorithms3–4 common arrangement | Shared state-cell stack, positive/equal/negative anchor partitions; recurse above anchor when quota exceeded, below when quota remains, finalize equal-boundary cells | Insert all remaining anchor comparisons at once, rather than incremental half-space insertion/Lemma1 pruning. Full equality cells prevent general-position assumptions from deleting tied members |
| UTK2 partition output | JAA-FD records each terminal state's constant tie-inclusive top-k set and then unions them | Primary comparison asks for the exact union; JAA's richer internal partition output is disclosed. A valid union-saturation shortcut may finish without constructing the richer partition |

Both screened finite controls receive the same existing feature/anchor safe
screen as screen+batch. Its cost is included independently in each pipeline.
They retain genuine regional-dominance and arrangement work after this
screen; they do not read old oracle unions or simply return a batch result.
Original parent/batch source is unchanged. All methods share only the warm
immutable index and common valid all-zero shortcut.

The support minimum is exact because each token choice independently sets
one factor, with only the shared count of changed original positions coupling
them. For margins m_ia, the minimum equals sum_i m_i0 minus the B largest
losses m_i0-min_a m_ia (raw included). Each choice attains its selected token
minimum, so this is neither a fractional bound nor an independence relaxation
across different documents. All integer operations are guarded against
overflow at the current factor sizes.

A record discarded for k strictly better records cannot be in the
tie-inclusive top-k at any state. If a previously discarded record dominates
a later one, its k retained strict ancestors also dominate that later record
by transitivity, so scanning retained records suffices. Sorting by a real
pivot score cannot put a strict regional dominator after its descendant.

RSA's remaining-state mask discards a state only after k strict superiors
are established. A drill or a completed mask supplies a concrete attaining
state. JAA's trichotomy fixes sets H,E,L in each cell: recurse on H if
|H|>=quota; return H unionE when |H|<quota<=|H|+|E|; otherwise include H
unionE and recurse on L with reduced quota. Every recursion removes the
anchor, covers all admissible states and retains equality sets at the cutoff.

These arguments and small exhaustive tests establish the intended adapter
semantics; the all-query independent sparse replay validates the actual
executions. They are not a formal verification of all numerical libraries.
Measured ratios apply to these instrumented Python/NumPy implementations,
including proof-receipt construction, not optimized C++ RSA/JAA or all
possible finite-domain UTK adaptations. This completion narrows the missing
matched-control issue; it does not prove global priority or Q1 acceptance.
