# Index-first certification experiment

Read PROTOCOL.md and THEORY.md before interpreting any speed comparison.
This work tests a bottleneck repair; it does not certify Q1 readiness,
algorithmic originality or SOTA ranking. Old studies remain unchanged.
Completed confirmation results are in [REPORT_VI.md](REPORT_VI.md).
The exact-certificate construction gate passed; the short-session speed
gate failed. See [CLAIM_DEFENSE_VI.md](CLAIM_DEFENSE_VI.md) for the claim boundary.

The recorded run uses Python3.12.14 and the pinned root requirements.txt.
Source pins/hashes
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

Audit the released records and rebuild the source index separately:

```sh
python -m lazy_cert_study.verify_archive lazy_cert_study/results/confirmation.jsonl.gz --phase confirmation
python -m lazy_cert_study.rebuild_wands_index --data /workspace/research-data/wands --output /tmp/rebuilt-index-check.json
```

THEORY_NOTES.md clarifies raw-query-dependent anchor selection without
changing the frozen algorithm or experiment. The reconstruction checker was
added after the method freeze and used after confirmation, never as a
candidate-selection or timing component. Data-dependent source hashes and
raw measurements are retained in results/.
