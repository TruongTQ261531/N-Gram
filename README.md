# Vietnamese n-gram robustness: reproducible research audit

Experimental candidate: **Collision-Aware Paired Consistency (CAPC)**. This project tests a hypothesis; it does **not** claim a novel, state-of-the-art or Q1-ready algorithm.

Read `REPORT_VI.md` for conclusions and exact limitations, `RELATED_WORK.md` for primary-source novelty checks, and `PROTOCOL.md` for the pre-test protocol and amendment. Reports distinguish measured results from future work. See RUN_CORRECTIONS.md and audit/ for the disclosed keyboard-generator defect and complete rerun. The final code/configuration was committed before corrected test-score analysis, while test execution was already in progress.

## Reproduce

Python 3.11+ recommended; the isolated memory profiler needs Linux or WSL because it reads /proc (recorded runtime/version details in `results/runtime.json`). CPU only; no torch, GPU or LLM service is required. Fixed one-thread numerical libraries in study.py. The download uses ordinary HTTPS and obeys the current environment's proxy/network policy.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python download_data.py
python test_integrity.py
python -u study.py select
python -u study.py evaluate
MPLCONFIGDIR=/tmp/ngram-mpl python -u analyze.py
python profile_inference.py
python audit_solver.py
python make_report.py
python verify_results.py --metrics-only
```

To verify the recorded metrics without re-training or downloading data:

```bash
pip install numpy==2.3.5 pandas==2.2.3
python verify_results.py
```

Full reruns use `--metrics-only` because newly generated runtime stamps/logs differ from the committed artifact checksums. Default verification validates the recorded artifact bytes as well as the metrics.

The original experiment ran `select` and verified `selection_freeze.json` BEFORE starting `evaluate`. Re-running selection after test outputs already exist records `test_predictions_exist=true`; this is an audit flag, not a fresh pre-test registration. Use a clean copy/new results folder for an actual fresh replication. Runtime stamps are recorded metadata, not a trusted third-party preregistration.

## What is included

- `study.py`, `noise.py`: train-only feature fitting, OOF ambiguity proxies, 9 model/ablation variants, validation-only hyperparameters, 5 train/noise run seeds, 27 test conditions.
- `results/metrics.csv`: every dataset/run/model/condition; macro-F1, accuracy and all class F1 values.
- `results/*_predictions.npz`: predictions `[run,condition,method,example]`, true integer labels, original CSV row IDs, method names and run seeds. Condition order is in `*_conditions.json`; label order in `dataset_labels.json`.
- `results/dev_search.json`, `selected.json`, `selection_freeze.json`: complete development search and locked configuration.
- `results/paired_bootstrap.csv`: paired document-cluster confidence intervals. All views/runs for an original example share its resampling count. These intervals are conditional on the fitted runs and synthetic generator, not a population of future training runs.
- `results/isolated_efficiency.csv`: post-training measurements in one fresh process per model, including full-pipeline batch=1 latency, batch throughput, loaded RSS and peak process RSS. `results/solver_audit.csv` records full-data seed-17 ridge normal-equation residuals.
- `results/efficiency.csv`: method-specific batch=1 end-to-end p50/p95 over 450 sequential timing measurements, fit time and serialized artifact size. Fit time excludes shared vectorization/augmentation; the recorded process peak RSS is not per-model inference memory.
- `results/data_audit.json`, `*_corruptions.json`, `fold_overlap_sensitivity.csv`: actual split counts, duplicates/conflicts, perturbation coverage and sensitivity checks.
- `results/reproducibility.json`: one true re-fit of seed 17 per dataset/model; clean predictions compared bit-for-bit.
- `verify_results.py`: independently reconstructs every F1/accuracy cell using confusion matrices directly from arrays.

All 9 methods share a character vocabulary/IDF fitted on raw and mechanically folded training text, including clean-only character baselines. Thus those baselines see unlabeled training-derived folded vocabulary, not development/test text. Word TF-IDF uses raw training only. Ridge is class-balanced and has no intercept. The system is an engineering pilot, not a fully tuned state-of-the-art benchmark.

## Data and limitations

Pinned public mirrors: `ura-hcmut/UIT-VSFC` and `ura-hcmut/UIT-VSMEC`. See `download_manifest.json` for exact revisions, URLs and SHA-256 hashes. Their dataset cards specify **CC BY-NC-SA 4.0**. Cite the original UIT dataset publications and retain their terms. Public availability is not unrestricted commercial permission. Source data, the user's Word file, checkpoints and example text are NOT committed here. Local review CSVs produced by evaluation are unverified synthetic examples and are ignored by Git.

`ViHSD` at the requested official location is gated and was NOT downloaded or tested. No Transformer was trained or timed. There is no human-validated new noise set, no novel task dataset, and no evidence here that every synthetic corruption preserves the label. Noise severity is a token-selection probability, NOT character edit distance. Teencode coverage is limited by a small fixed dictionary; keyboard errors are simple neighbor substitutions, not an empirically fitted Vietnamese input-method model. Wrong-tone changes can alter meaning. NFD is only a Unicode-normalization sanity check. Clean data itself may already contain natural social-media noise.

Dataset cardinalities/cleaning and algorithm failures are disclosed. More runs cannot compensate for a missing real-world validity check or insufficient novelty.
