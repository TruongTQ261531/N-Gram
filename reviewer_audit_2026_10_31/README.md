# Reviewer supplement after network recovery

All 20 original source files were restored byte-for-byte. Rebuilt model
fingerprints match the frozen indexes. The supplementary MILP/controlled
runtime study is COMPLETE on all 970 original query IDs. These additions
are retrospective and do not replace the original confirmations.

| Corpus | n | BestLP+enum | Discrete | MILP+enum |
|---|---:|---:|---:|---:|
| SciFact | 199 | 115 | 123 | 123 |
| NFCorpus | 223 | 41 | 45 | 47 |
| FiQA | 548 | 71 | 91 | 90 |

Read RESPONSE_VI.md,PROTOCOL.md,BRIDGE_AMENDMENT.md,
VERIFICATION_ADDENDUM.md and CLOSEST_METHODS.md. Current results include
all-query first-pass bounds/timing, fixed repeated-subset diagnostics,
solver statuses, paired comparisons, and larger-cap verification-only
checks on ALL three-method coverage-discordant queries. Original caps,
source files, results, query IDs and failed session gates are unchanged.

The existing 128-query/6,684-state WANDS bridge remains retrospective.
Native UTK RSA/JAA reports are a three-record continuous-domain fixture,
with upstream failure and guard-corrected variant retained separately.
They are NOT a matched NLP baseline or an SOTA claim. Third-party source,
binaries, PDFs, raw corpora, caches and manuscript files remain outside Git.
The same research branch is used; no additional branch is created.

Historical network-blocked snapshots remain under
results/history/pre-network-revision7; current results supersede the old
unmeasured status without erasing that history. Network access no longer
blocks source restoration.

Install the pinned numerical/Parquet dependencies in round3/requirements.txt.
The corpus cache is external. Reproduce the audit with:

```sh
python -m unittest discover -s reviewer_audit_2026_10_31 -p 'test_*.py' -v
python -m reviewer_audit_2026_10_31.check_archive
sha256sum --quiet -c reviewer_audit_2026_10_31/checksums.sha256
python -m reviewer_audit_2026_10_31.analyze --runs reviewer_audit_2026_10_31/results/retention --output /tmp/supplement-analysis.json
```

For full re-evaluation, use restore_data,retention,verify_discordant and
native_utk module CLIs. Run timed datasets sequentially, one numerical
thread, with no other study benchmark/compilation. native_utk requires a
separately obtained private UTK build with the documented IO harness;
source access and redistribution remain subject to its upstream notice.
Missing or inconclusive checks never become fabricated negative outcomes.
