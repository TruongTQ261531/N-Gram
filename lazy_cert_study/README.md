# Index-first certification experiment

Read PROTOCOL.md and THEORY.md before interpreting any speed comparison.
This work tests a bottleneck repair; it does not certify Q1 readiness,
algorithmic originality or SOTA ranking. Old studies remain unchanged.

Use Python3.11 with numpy, scipy, scikit-learn and pandas. Source pins/hashes
are in sources.json; the index is built from all products with the parent's
unchanged integer scorer. Keep large downloads outside Git:

```sh
python -m lazy_cert_study.fetch_wands --data /workspace/research-data/wands
python -m lazy_cert_study.prepare_wands --data /workspace/research-data/wands
python -m unittest lazy_cert_study.test_core -v
python -m lazy_cert_study.benchmark --data /workspace/research-data/wands --phase development --repeats 1 --output /tmp/development.jsonl.gz
python -m lazy_cert_study.analyze /tmp/development.jsonl.gz --output /tmp/development-analysis.json
```

Confirmation additionally requires a frozen, committed method/protocol and
confirmation_freeze.json. Never label a rerun after reading confirmation as
an independent validation. Outputs refuse to overwrite files. Request and
oracle checks are outside timing. Preprocessing/index loading is shared and
reported separately; per-query initialization is included.

The study contains no LaTeX/BibTeX manuscript or figures, by user request.
