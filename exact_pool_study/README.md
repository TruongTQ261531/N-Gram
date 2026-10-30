# Compiled bounds and exact finite-edit unions, separate research branch

This branch extends main94a9f0c without changing its published scientific data or live website. It addresses repeated certificate work, conservative pool slack, truncated long queries and whole-session measurement. The project-wide Vietnamese inventory is [PROJECT_REVIEW_2026-10-30.md](../PROJECT_REVIEW_2026-10-30.md).

- [New outcome report](REPORT_VI.md), [all results](results/), [descriptive summary](results/analysis.json)
- [Primary prospective protocol](PROTOCOL.md), [primary freeze](freeze.json), [32 unseen-query selections](selection.json)
- [Supplemental ordinary-memoization/session protocol](SESSION_ADDENDUM.md), [its separate freeze](session_freeze.json)
- [Factor-construction engineering audit](FACTOR_ADDENDUM.md), [its separate freeze](factor_freeze.json)
- [Proof and exact scope](THEORY.md), [bounded novelty assessment](RELATED_WORK.md)

Primary code/selection was publicly pushed at70629444f90c1841f1562aba4e1a2121f59455a8 before its new outcomes. Supplemental timing code was pushed at2a05551 before its timings but after the primary experiment started; it is not a new independent confirmation dataset. Original results are retained. Sources/weights match the parent pinned public corpora; no new training, qrels, human or LLM relevance annotation.

## Published-artifact verification

```bash
pip install numpy==2.3.5
python exact_pool_study/check_archive.py
```

This checks all three source freezes, data/selection/maps, independently validates whole-corpus exclusions and group coverage, independently enumerates original states on the safe projection, verifies every saved quotient output and witness, and checks all measured session answers. It does not download corpora; source-replay receipts record an additional independent reconstruction from the original stored index postings.

## Source tests and new runs

```bash
pip install -r pool_study/requirements.txt
python exact_pool_study/test_method.py
python exact_pool_study/test_fast_factors.py
```

For recomputation use a separate checkout and MOVE its `exact_pool_study/results` directory outside that checkout first, preserving the published evidence. The generators refuse overwrites. Download/build the pinned original indices using the parent pool_study instructions, or reuse indices built by your own trusted run. The mathematical target is the resulting canonical integer-weight hash, not every platform's floating log implementation.

```bash
python exact_pool_study/run.py --data /absolute/path/to/pool-data --dataset arguana
python exact_pool_study/run.py --data /absolute/path/to/pool-data --dataset scidocs
python exact_pool_study/session_audit.py --data /absolute/path/to/pool-data --dataset arguana
python exact_pool_study/session_audit.py --data /absolute/path/to/pool-data --dataset scidocs
python exact_pool_study/factor_audit.py --data /absolute/path/to/pool-data --dataset arguana
python exact_pool_study/factor_audit.py --data /absolute/path/to/pool-data --dataset scidocs
python exact_pool_study/verify.py --dataset arguana --output new-arguana-verification.json
python exact_pool_study/verify.py --dataset scidocs --output new-scidocs-verification.json
python exact_pool_study/replay_sources.py --data /absolute/path/to/pool-data --dataset arguana --output new-arguana-source-replay.json
python exact_pool_study/replay_sources.py --data /absolute/path/to/pool-data --dataset scidocs --output new-scidocs-source-replay.json
```

Do not benchmark datasets concurrently. A new run's timestamps/timings/NPZ compression bytes can differ, so the published checksum verifier is for the original archive; `verify.py` checks a newly generated experiment's arithmetic/outputs separately. The actual partial/full session measurements include new-query factors/certificates/subset construction; shared warm corpus-index loading is excluded equally from all methods.

## Data and code rights

Original ArguAna/SciDocs queries and derived forms/scores/oracles retain upstream attribution and CC BY-SA4.0 notices as specified in [pool_study/DATA_LICENSE.md](../pool_study/DATA_LICENSE.md). Changes here add full-query evaluation, the fixed new selections, compiled/exact methods, quotient proof states and controlled sessions. These are inherited real texts with synthetic compact errors, not natural typo logs, new relevance labels or newly collected original corpora. No visitor data was collected. New code is MIT under [pool_study/CODE_LICENSE](../pool_study/CODE_LICENSE).

Algorithmic equivalence/symmetry/bounds have prior art. Mathematical correctness, application usefulness, dataset contribution, global novelty and Q1 acceptance remain separate claims. See REPORT_VI for negative controls, resource limits, workload limitations and the current decision.
