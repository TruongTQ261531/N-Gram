# Reproducibility

Run commands from the repository root. Python 3.12 on Linux is the supported recorded scientific environment. Install `requirements-all.txt` in a virtual environment; it includes the pinned root, BOLT and pool dependencies. No GPU, paid API or new human annotation is required for archive verification.

## 1. Verify the published records offline

```bash
python -m pip install -r requirements-all.txt
python verify_all.py
```

This runs 16 archive checks covering CAPC, BOLT, retention, application, pool, exact pool, index-first development and confirmation, reviewer/decision audits, UTK adapters, graph/neural follow-up, claim consolidation, full-domain UTK controls and both November 5 follow-ups. It checks integration/release hashes and calls the existing scientific verifiers. It neither downloads raw data nor executes new optimization benchmarks. Python assertions must be enabled; do not use `python -O` or `PYTHONOPTIMIZE`.

Release checksums include some documentation and packaging files. The maintenance record distinguishes their updated hashes from unchanged experimental source freezes, selection locks and numerical evidence. A matching checksum establishes byte identity, not scientific validity by itself.

## 2. Run component tests

```bash
python round3/verify_freeze.py
python -m unittest discover -s round3 -p 'test_*.py'
python -m unittest discover -s reviewer_audit_2026_10_31 -p 'test_*.py'
python -m unittest discover -s decision_audit_2026_10_31 -p 'test_*.py'
python exact_pool_study/test_method.py
python exact_pool_study/test_fast_factors.py
python pool_study/test_core.py
python -m unittest lazy_cert_study.test_core -v
python -m unittest utk_adapter_study.test_adapter -v
python -m unittest argon_followup_2026_11_01.test_graph argon_followup_2026_11_01.test_multiword -v
python -m unittest claims_consolidation_2026_11_01.test_routing -v
python -m unittest utk_full_domain_2026_11_01.test_algorithms utk_full_domain_2026_11_01.test_archive -v
python -m unittest codex_followup_2026_11_05.test_experiments -v
python -m unittest self_review_2026_11_05.test_graph_review -v
```

Run the study commands in separate Python processes as shown: several frozen modules use the same legacy top-level import names (`core`, `method`). Combining unrelated suites in one process can load the wrong module.

Node.js 24 is used for the browser engine tests, with no npm dependency installation:

```bash
node webapp/test-engine.mjs
node webapp/test-pool.mjs
```

The [GitHub workflows](../.github/workflows/) also retain historical CAPC/BOLT checks. Some historical workflows acquire external datasets; passing offline archives does not imply that every upstream download remains available.

## 3. Re-execute scientific experiments

**Use a separate working copy.** Preserve archived outputs elsewhere before creating new results. Do not regenerate the published checksums to conceal a mismatch, overwrite frozen evidence or call an already-viewed sample a new independent confirmation. Existing raw scripts may refuse to overwrite result files.

Each stage has its own protocol, source hashes, query IDs, input fingerprints and environment receipts. Follow the relevant guide:

| Stage | Re-execution instructions |
| --- | --- |
| Central retention and original replication | [round3/REPRODUCE.md](../round3/REPRODUCE.md) |
| Offline exact pool | [exact_pool_study/README.md](../exact_pool_study/README.md) |
| Index-first WANDS audit | [lazy_cert_study/README.md](../lazy_cert_study/README.md) |
| Full-domain finite RSA/JAA controls | [utk_full_domain_2026_11_01/README.md](../utk_full_domain_2026_11_01/README.md) |
| Sensitivity panel and exact oracle | [codex_followup_2026_11_05/README.md](../codex_followup_2026_11_05/README.md) |
| Full-cohort graph replay and support probe | [self_review_2026_11_05/README.md](../self_review_2026_11_05/README.md) |
| Historical CAPC/BOLT and application | [legacy reproduction guide](LEGACY_REPRODUCE_VI.md) |

Restore pinned raw distributions and indexes from the upstream links/manifests in those guides, accepting their respective distribution terms. Set `DATA_ROOT` to that restored research-data root for scripts accepting `--data`; do not substitute an unrelated cache or unpinned model. Raw corpora, index pickles and restricted UTK dependencies are intentionally absent from Git.

Use one numerical thread where the protocol specifies it:

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
```

Do not benchmark concurrently. The original runtime receipts describe their own CPU/RAM limits, warm indexes, solver caps and repetitions. A small test can pass while full-corpus runs need substantially more memory; the November 5 sensitivity run used a 32 GiB limit and an explicit dense-cell cap. New wall times, capped numerical solver outcomes and compressed byte hashes need not match the archived run. Preserve and explain differences. Follow the stage-specific instructions to generate a separate manifest for new outputs.

No single rerun command establishes lexical relevance, neural robustness, global novelty or acceptance by a journal. See [Results and scope](RESULTS_AND_SCOPE.md) for the supported comparisons.
