# Verification and CPU reproduction

Use Python 3.12 and the pinned packages. No GPU, paid API, fresh annotations or LLM judge is required. A new local run is a replication of known evidence, not a new untouched confirmation. The predictor source and two original preregistration files must not be rewritten to make a rerun look prospective.

## 1. Verify the published evidence offline

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-all.txt
python verify_all.py
python -m unittest discover -s round3 -p 'test_*.py'
```

`verify_all.py` checks the three studies, manifests, source/configuration hashes, per-query metrics, individual sampled predictions, saved bootstrap draws, exact paired tests and Holm adjustments. It does not download data or fit models. Offline recorded checks need only numpy/pandas; numerical tests need scipy and the pinned scientific stack. The unit tests and CI are implementation evidence, not a formal proof of all compiled code or novelty.

To cross-check the released real-query margin fixtures numerically:

```bash
python round3/audit_fixtures.py
```

This reruns generic LP/MILP and small-lattice enumeration from NPZ matrices without corpus pickles. Runtime fields/new solver traces may differ; this command overwrites only the local fixture diagnostic output. Use a separate checkout for regenerated files.

## 2. Download pinned data and build the full indexes

For full inference/recomputation, use a separate clone. The downloaded bytes are checked against pinned upstream revisions; all corpus documents are indexed. Do not use a small candidate subset as an undisclosed replacement.

```bash
export OMP_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
python round3/download.py
python round3/run.py prepare --dataset scifact
python round3/run.py prepare --dataset nfcorpus
python round3/run.py prepare --dataset fiqa
python round3/verify_freeze.py
```

Set thread variables BEFORE Python/numpy starts. This corrects the original confirmation import-order execution deviation without modifying its frozen predictor. The managed run used a two-core quota/8 GiB RAM. At least 8 GiB with one dataset process is sensible; 16 GiB gives more margin for independent parallel reruns. The largest controlled primary process peaked near 3.68 GiB. Index/startup and building may require additional memory and time. A faster local CPU increases experimental throughput, not the language model's reasoning ability.

## 3. Certify a new query without labels

```bash
python round3/certify_query.py --dataset scifact --query 'vitamin deficiency affects bone growth' --budget 2 --k 10
```

The JSON gives the clean reference document ID, conservative rank upper bound, retention flag, truncation and certificate trace. It does not predict whether the reference is relevant. The finite edit model is specified in the output and protocols. A false retention flag means unknown from this bound, not a demonstrated attack.

## 4. Recompute the original 300-query stage

Use a separate clone and copy the entire original `round3/results/` and its checksum manifest to an evidence backup OUTSIDE the working folder before recomputation. Keep all frozen source/selection metadata in place. Experimental drivers may overwrite stage-one outputs; the replication driver refuses to overwrite its outputs. Do not remove the backup or silently replace the public originals.

```bash
python -u round3/experiment.py --dataset scifact --phase confirmation --limit 100 --label confirmation
python -u round3/experiment.py --dataset nfcorpus --phase confirmation --limit 100 --label confirmation
python -u round3/experiment.py --dataset fiqa --phase confirmation --limit 100 --label confirmation
python round3/analyze.py
```

These commands run the matched LP/MILP/enumeration controls and seeded attacks. For a quick arithmetic smoke run, change `--limit 100` to `--limit 3` and `--label confirmation` to `--label local_smoke`; do not analyze this as a new confirmation sample.

Replay/export individual predictions and controlled timing, sequentially with no other heavy CPU job:

```bash
python -u round3/replay_all.py
python round3/verify_predictions.py
```

The replay compares deterministic bounds and sampled diagnostics. A different platform may produce conservative floating-bound/solver-termination differences; preserve every discrepancy and environment rather than changing records to match. Wall times, peaks and complete JSONL byte hashes are not expected to match a rerun. The published primary-results lock refers to the original run, so it must not be replaced and falsely described as still prospective. Metric-vector comparisons against the backup are more meaningful than expecting runtime-containing JSONL hashes to match.

## 5. Recompute the independent 970-query stage

Keep the committed `replication_ids.json`, `replication_freeze.json`, source and `primary_results_lock.json` unchanged. In the separate recomputation clone, move the three `*_independent_replication.jsonl`/`.gz` originals to the backup before running. Do not call `prepare` or `freeze` to redefine the sample.

```bash
python -u round3/replication.py run --dataset scifact
python -u round3/replication.py run --dataset nfcorpus
python -u round3/replication.py run --dataset fiqa
python round3/analyze_replication.py
```

The full FiQA command can run sequentially; the original execution-only partition amendment is retained for provenance but is unnecessary on a new machine. The original published evidence verifier intentionally rejects changed byte hashes. Use the backup to check predictor/metric agreement, and identify new runtimes as your own execution. Do not pool stages or treat these already-viewed inputs as a new independent validation dataset.

## Files and semantics

- JSONL.gz is ordinary gzip of complete original UTF-8 records; uncompressed primary hashes are in `primary_results_lock.json`. Every selected query is present, including ties/OOV/resource skips.
- `*_individual_predictions.npz` stores query/document IDs, alternative-state choices, state sizes, observed strict ranks, top document indices and qrel grades for all 27,000 sampled attacks. Indices refer to its own `document_ids` array. Padded token choices are zero; only up to B are nonzero.
- Bootstrap NPZ files hold exact sampling indices; CSVs hold both stages separately. A sampled strict rank is an observed lower diagnostic and can be smaller than worst-tie rank.
- Certificate records include LP/support history, graph edge proofs/groups, enumeration and numerical solver outcomes. A cap/timeout is unknown; it is not a negative example or omitted query.
- The original primary freeze has 17 files; the independent-stage freeze locks 23 files. `replication_range.py` checks its per-query source identity with the frozen driver. Input-text SHA256 checks are reproducible from pinned queries without publishing their text.
- Raw corpus, query text, full cache pickles, literature full text and the uploaded Word file are excluded. See DATA_LICENSE.md.
