# Reviewer-requested claim and numerical-contract audit

Read [RESPONSE_VI.md](RESPONSE_VI.md), [PROTOCOL.md](PROTOCOL.md), and
[BRIDGE_AMENDMENT.md](BRIDGE_AMENDMENT.md). All new evaluations are
retrospective; original source/freezes/results remain unchanged.

Completed: common-feature quantization bridge and exact-boundary/casefold
refinement on128 previously observed WANDS queries/6,684 states; archived
runtime provenance audit; small/existing-fixture tests of the supplement.
Blocked: full970 MILP/controlled timing due missing historical raw data;
original UTK RSA/JAA comparison due unavailable verified source/contract.

Use root numerical dependencies and round3/requirements.txt for Parquet.
Keep downloaded sources and index caches OUTSIDE Git. Manuscript files also
remain outside this repository, per the user's request.

```sh
python -m unittest discover -s reviewer_audit_2026_10_31 -p 'test_*.py' -v
python -m reviewer_audit_2026_10_31.bridge --data /workspace/research-data/wands --output /tmp/bridge.jsonl.gz
python -m reviewer_audit_2026_10_31.bridge_refinement --data /workspace/research-data/wands --output /tmp/bridge-refined.jsonl.gz
```

After the saved environment network draft has been reviewed/published:

```sh
python -m reviewer_audit_2026_10_31.restore_data --data /workspace/research-data/round3-restored --fetch --report /tmp/restoration.json
python -m reviewer_audit_2026_10_31.retention --data /workspace/research-data/round3-restored --dataset scifact --output /workspace/research-data/reviewer-audit/retention/scifact.jsonl.gz
python -m reviewer_audit_2026_10_31.retention --data /workspace/research-data/round3-restored --dataset nfcorpus --output /workspace/research-data/reviewer-audit/retention/nfcorpus.jsonl.gz
python -m reviewer_audit_2026_10_31.retention --data /workspace/research-data/round3-restored --dataset fiqa --output /workspace/research-data/reviewer-audit/retention/fiqa.jsonl.gz
python -m reviewer_audit_2026_10_31.analyze --runs /workspace/research-data/reviewer-audit/retention --output /tmp/supplement-analysis.json
```

Run dataset timing jobs SEQUENTIALLY with no competing study benchmark.
Check SHA256 source/model fingerprints and frozen-rank agreement before
interpreting any supplementary result. Outputs refuse silent overwriting.
Missing coverage/timing is unmeasured; it is never filled using old aggregate
logs, a theoretical domination assumption, or fabricated data.
