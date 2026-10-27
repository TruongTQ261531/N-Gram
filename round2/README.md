# BOLT: Budgeted Orthographic Lattice Training — research candidate

BOLT is a contextual sparse classifier and exact, budget-constrained adversarial oracle, with a convex robust-training surrogate. It is an implemented experimental method, not merely a collection of baseline scores. It is **not a verified globally novel or Q1-ready algorithm**. See NOVELTY.md for closest prior art and THEORY.md for exact claims and their limits.

The experiment uses existing labels only. No new human annotation or semantic-equivalence certification is claimed. The robustness guarantee is prediction invariance over the specified orthographic lattice; it does not assert literal meaning preservation.

Read [REPORT_VI.md](REPORT_VI.md) for the final outcome: useful exact-oracle properties and robustness gains over random augmentation, with Q1-level novelty/readiness **not established**.

## Reproduce from repository root

Python 3.12 was used. CPU, one numerical thread. Install the pinned dependencies into a virtual environment.

```bash
pip install -r round2/requirements.txt
python download_data.py
python round2/download_fr.py
python round2/test_lattice.py
python round2/run.py prepare
python -u round2/run.py select
python -u round2/run.py final
```

`select` must complete and freeze its configuration before viewing French confirmation scores. Vietnamese test scores were already inspected in the prior CAPC study, so new Vietnamese results are explicitly exploratory. French train/validation/test subsets are deterministic and their row IDs are recorded. French test has 1999 retained rows after removing one duplicate against the chosen splits.

The feature vocabulary/IDF is fitted on training-derived token forms only. New forms seen at evaluation are transformed with fixed statistics, not fitted. The first 128 whitespace tokens are retained for every method. The encoder stores a speed cache of transformed forms; cache indices are not learned features and hashes depend on actual strings, so adding test forms does not change previously encoded model scores.

## Mathematical and empirical checks

- Exact weighted-budget dynamic programming with contextual pair factors and attaining witness.
- 600 differential comparisons with exhaustive search, including variable costs, invalid states, budget zero and negative weights.
- A contextual counterexample where greedy misses the joint attack.
- Feature-factorization equality, canonical invariance, budget monotonicity and finite-difference training gradients.
- Full source/parameter freeze before independent French test analysis.
- Save every seed's labels, row IDs, predictions, certified margins and diagnostic arrays; independently reconstruct metrics.
- Export seed-17 BOLT models as numerical `.npz` arrays, without pickle or corpus caches; independently reload and re-run certification.

## Important scope

Variants are raw, tone-folded and fully folded forms, coalesced and restricted to the same NFC codepoint length. Budget counts changed NFC codepoints. Length-changing cases such as standalone combining marks retain raw-only forms; preparation caught this before training and the correction is logged. Arbitrary edits, insertions/deletions, synonyms, general Levenshtein balls and unknown semantic transformations are outside the guarantee. Hash collisions do not invalidate the oracle because both scoring and oracle use the same additive factors.

L-BFGS and witness rounds have finite iteration caps. An exact separation oracle does not imply that robust training reached the global optimum. Full optimizer status, gradient norm and separation gap are saved.

Closest broad methods include ARC (EMNLP 2021), certified word-substitution training (EMNLP 2019) and LipsLev (ICLR 2025). The underlying DP/convex-optimization machinery is established. Narrow implementation-specific novelty still needs a convincing closest-method comparison; better scores alone would not prove Q1 novelty.

## Verify recorded results without downloading source corpora

```bash
python round2/verify_recorded.py
python round2/test_lattice.py
python round2/test_dual.py
```

Recorded checksums are checked before tests, because the randomized oracle test regenerates its own diagnostic file. For a fresh full reproduction after `run.py final`, run `verify.py`, `audit_milp.py`, `analyze.py`, `audit_optimization.py`, `dual_audit.py`, `profile.py` and `report.py` (all inside round2/). Use `verify_recorded.py --skip-checksums` for newly generated output bytes; runtime stamps and logs differ from the recorded archive. The profiler needs Linux/WSL.

The optional primal-dual routine is a development-only convergence audit, not substituted into the frozen test models. Training logs preserve iteration-limit status. `eta` is ignored and set to zero for clean/canonical methods, as defined in PROTOCOL.md. Data/model terms are in DATA_LICENSE.md.
