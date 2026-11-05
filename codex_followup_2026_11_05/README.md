# IP&M claim follow-up — 5 November 2026

This folder contains **retrospective validation of existing methods**, not a new scorer or corpus. Base main: `63ceeda350a0f7e3c9138c3b1232d2ea06e49054`. Local branch: `research/ipm-followup-2026-11-05`. Manuscript TeX/Bib/PDF files are maintained outside this repository.

Start with [EXPERIMENT_REPORT.md](EXPERIMENT_REPORT.md), [EXPERIMENT_PLAN.md](EXPERIMENT_PLAN.md) and [results/claims_matrix.csv](results/claims_matrix.csv).

## Results

- Metadata join: all 970 original IDs, LP227 / Discrete259 / later numerical MILP260; verified labels266 robust /704 nonrobust. No new full-970 solver run is claimed.
- New sample: 36 hash-selected, length-stratified queries; 684 fresh pipelines; 2,736 K-threshold decision rows. B2K10 pair/LP/Discrete/MILP =11/13/15/14. B3K10 =10/10/11/12. All unknowns stay in denominators.
- Support-only graph gives14 at B2K10 vs full15, but19 at K20 vs full18. Resource-bounded scheduling prevents monotonic coverage dominance.
- Removing LP/enum preserves15 binary B2K10 certificates while weakening12/one rank bounds. Do not claim each component is necessary.
- Tiny-domain independent exact-dyadic oracle: 396 checks, zero unsound bounds,185 nonvacuous positive method-budget outcomes.
- The failed historical session gate and neural transfer limits remain unchanged.

## Read-only verification

From the repository root, using Python3.12 with the recorded numerical environment:

```bash
python -m codex_followup_2026_11_05.verify
python -m unittest codex_followup_2026_11_05.test_experiments -v
```

`verify` checks source/sample hashes, joins, outcome counts, cap handling, full selected-query denominators and exact-oracle receipts. It does not contact the network, rerun solvers or rewrite historical artifacts. `FREEZE.json` records the pre-run local panel freeze; it is not an externally registered prospective protocol. `MANIFEST.json` hashes the final follow-up files separately.

## Re-execution

Use a separate fresh working copy; preserve the published `results/` directory elsewhere in that copy and create an empty `results/` before rerunning. Original repository archives must remain available at their existing relative paths. The raw run scripts refuse to overwrite existing gzip or oracle-case files. Do not run heavy benchmarks concurrently. Restore the pinned datasets/indexes from inherited manifests, and set `DATA_ROOT` to the restored research-data root.

```bash
python -m codex_followup_2026_11_05.extract --data "$DATA_ROOT"
python -m codex_followup_2026_11_05.run --data "$DATA_ROOT"
python -m codex_followup_2026_11_05.soundness
python -m codex_followup_2026_11_05.analyze
```

Analyze/verification of a fresh run should use its own manifest; do not expect new latency-sensitive solver results or byte hashes to equal the published receipts. The frozen one-second MILP reference may vary with host load. Original B2 LP/Discrete bounds must replay; unexplained mismatches block interpretation.

The completed run used Python3.12.14, NumPy2.3.5, SciPy1.17.0 and scikit-learn1.8.0, one numerical thread, a four-CPU quota and32GiB limit. It finished684 pipelines in389.15 seconds of study wall time. See [RUNTIME_ANALYSIS.md](RUNTIME_ANALYSIS.md) for the added20M dense-cell cap, sampled process RSS and timing limitations; historical missing stage/memory metrics are not imputed.

## Records

`results/query_level.csv` and `disagreement_cases.csv` cover the complete original cohort and every coverage disagreement. `runtime_per_query.csv` retains all archived repeats; `runtime_summary_970.csv` uses the complete first pass. `ablation_records.jsonl.gz` contains fresh proof/stage receipts; `ablation.csv` and `sensitivity.csv` are flat exports. `correctness_cases.jsonl` includes complete tiny-domain inputs and exact worst-state witnesses. Public logs and manifests preserve validation provenance without shipping raw corpora or manuscript files.
