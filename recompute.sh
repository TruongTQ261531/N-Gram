#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
export OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1
export MPLCONFIGDIR="${TMPDIR:-/tmp}/ngram-mpl"
python download_data.py
python test_integrity.py
python -u study.py select
python -u study.py evaluate
python -u analyze.py
python profile_inference.py
python audit_solver.py
python make_report.py
python verify_results.py --metrics-only
