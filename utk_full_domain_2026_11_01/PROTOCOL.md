# Matched finite-domain UTK controls — 1 November 2026 (Asia/Saigon)

Base: origin/main d2742e2 (merged claims-consolidation PR8). This is a
retrospective baseline completion, not a new novelty contribution. Earlier
freezes, primary tests and adverse results remain unchanged. Manuscript files
stay outside Git; no figure artwork is created.

## Target and attribution

Use all128 original WANDS confirmation IDs, all42994 products, the unchanged
stored integer/lowercase scorer, full queries, compact alternatives, B2/k10
and ALL admissible correlated states, with all kth-score ties. No selected
segments, token projection, convex box or outcome-dependent filtering.

Implement two independently written finite-domain adaptations of Mouratidis
and Tang, PVLDB2018, DOI10.14778/3204028.3204031:

* Screen+RSA-FD: exact regional strict dominance/k-skyband filtering, then
  candidate-specific arrangements over admissible states, decreasing
  dominance-count verification and propagation to strict ancestors.
* Screen+JAA-FD: the same filter, then one shared arrangement with the kth
  pivot anchor, less/equal/greater recursion and explicit equality cells.

Sections4.1–4.3 and5.1–5.2/Algorithms3–4 of the primary paper guide the mapping.
Finite bitsets/state sets replace convex cells and LP feasibility. Complete
anchor comparisons replace the paper's incremental half-space insertion;
strict dominance/equality cells adapt the original general-position target
to this manuscript's tie-inclusive output. The finite implementations use
NumPy/Python and the same fixed scorer; they are NOT original C++ RSA/JAA,
not a runtime reproduction of their continuous-region experiments, and not
claimed as fully optimized implementations of every paper optimization.
Original source conformance/segment diagnostics remain separately reported.

Strict regional dominance p>q means min over the ENTIRE finite domain of
S_p-S_q is positive. The minimum is computed exactly from integer token
factors: raw margin minus the B largest nonnegative token losses. Thus
ties never remove a possible boundary member. A discarded document stores
k strict dominators and positive margin minima. Surviving candidates retain
the full original scores; weights are never refitted or quantized again.

## Matched controls and timing

Compare against unchanged lazy_cert_study.benchmark.build parent and
screen_batch. All methods may use the same all-zero union shortcut; the
three screened methods may use identical safe screen and raw-pool saturation.
Record these shortcuts explicitly. They are full-domain proofs, not omitted
queries. JAA-FD builds constant top-k cells when its union shortcut does not
finish; its richer internal output is disclosed rather than hidden.

Each method independently includes lattice construction, screening where
applicable, factor materialization and refinement. Only the immutable warm
index is shared; source loading/index load are excluded. Fixed hash-rotated
order, three executions per query, datasets/jobs sequential, one numerical
thread and no concurrent benchmark. Keep every repeat, take its median per
query. A repeat is not a new query or an independent confirmation sample.

Each finite adapter has a120-second soft wall guard, checked between proof
blocks/partitions, a50million state-score-cell cap and a1million arrangement-
node cap. A cap returns the safe screened superset marked resource_unknown,
never an exact union. Record every cap/failure and whole-pipeline time; do
not discard capped cases. Existing parent/batch limits remain unchanged.
No primary gate is revised. Report descriptive per-query costs, geometric
ratios only for controls completing the SAME exact target, and coverage of
the full128 denominator. No new SOTA or primary significance claim.

## Validation and publication

Freeze IDs/source hashes and unit-test the tie/budget/arrangement semantics
before measurements. The timing runner never reads the old oracle unions
or neural/robustness labels. After timed execution, independently replay
EVERY admissible state with the original full-corpus sparse text scorer,
then compare each completed method union and JAA's state-cell outputs.
Retain state hashes, top-k IDs, union and original index/source hashes.
Check all completed repeats, not only a best run. Unit fixtures additionally
compare both adapters with direct enumeration on random small factors,
budget-correlation cases, tied boundaries and resource-cap safety.

Publish our code, numeric proof/partition receipts, IDs/hashes, all runtime
records, analysis and an explicit paper-to-implementation mapping. Original
third-party source/binaries, raw texts and indexes remain outside Git.
The comparison addresses the exact finite-channel workload, not equivalence
or priority against all UTK adaptations or all discrete verifiers. It cannot
guarantee Q1 acceptance. Preserve the failed original session gate and all
existing lexical-to-neural transfer limitations.
