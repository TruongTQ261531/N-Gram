# Shared-query retention certificates

This stage contains the central float64 character-n-gram retrieval certifier and its original 300-query confirmation and independent 970-query replication. It certifies retention of the clean-query winner in top-K under the declared finite shared per-token edit channel; it does not improve relevance scores.

## Current results

At B=2, K=10 on the independent 970 queries, original Best LP + enumeration certifies 227 and original Discrete certifies 259. The later numerical MILP control certifies 260. Later exact-decision auditing labels 266 robust and 704 nonrobust cases. Optional refinement reaches all 266 robust cases in a retrospective replay with added cost; it does not replace the original counts or tests.

The original LP comparison passes the prespecified Holm-adjusted tests on SciFact and FiQA, not NFCorpus. The ten-query-per-corpus timing pilot in the original report is historical; see the current [results guide](../docs/RESULTS_AND_SCOPE.md) for the full-cohort timing audit, method disagreements and limitations.

Start with [THEORY.md](THEORY.md), [PROTOCOL_RETENTION.md](PROTOCOL_RETENTION.md), [PROTOCOL_REPLICATION.md](PROTOCOL_REPLICATION.md) and [REPRODUCE.md](REPRODUCE.md). [REPORT_VI.md](REPORT_VI.md), [NOVELTY.md](NOVELTY.md), [RELATED_WORK_UPDATE.md](RELATED_WORK_UPDATE.md) and [RUN_HISTORY.md](RUN_HISTORY.md) preserve the original stage's dated interpretation. Manuscripts and bibliography files are maintained outside Git.

## Offline checks

From the repository root, using Python 3.12 and the pinned dependencies:

```bash
python round3/verify_freeze.py
python round3/verify_archive.py
python -m unittest discover -s round3 -p 'test_*.py'
```

These verify recorded source/selection locks, rank bounds, independent replication and 27,000 sampled prediction records without raw corpus downloads. Use `python verify_all.py` for the complete current archive, including later audits.

## New queries and re-execution

Restore the pinned corpus and local index as described in [REPRODUCE.md](REPRODUCE.md). Run from the repository root:

```bash
python round3/certify_query.py --dataset scifact --query 'vitamin deficiency affects bone growth' --budget 2 --k 10
```

The corpora contain 5,183 / 3,633 / 57,638 documents (SciFact / NFCorpus / FiQA). The contract uses NFC/casefold normalization, at most 32 tokens, conservative ties and the finite delete/swap/repeat/QWERTY channel. Numerical enclosures rely on the documented IEEE-754 and sparse-dot assumptions; the compiled numerical stack is not formally verified.

Do not overwrite archived outputs. Use a separate working copy for new runs and preserve the freezes. `build_report.py` rebuilds only the historical Vietnamese report from its original records; it does not regenerate a manuscript or replace this maintained README. See [data terms](DATA_LICENSE.md) before acquiring or redistributing upstream material.
