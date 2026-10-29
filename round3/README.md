# Discrete shared-query certificates for n-gram retrieval

Research round 3, 29 October 2026. A working inference-time certifier for a fixed character-BM25 ranker, with full-corpus experiments, an initial 300-query confirmation and a separately preregistered 970-query replication. **Originality and Q1 readiness remain unconfirmed.** CAPC/BOLT scientific results remain unchanged; no unevaluated hybrid is claimed.

The method certifies that the original winner stays in top-K under a finite common-query token-edit model. It uses safe screening, exact pairwise margins, a matched affine LP and discrete incompatibility covers, with feasible enumeration and generic LP/MILP controls. It does not improve the underlying relevance scores. LP, DP, coloring, pruning and top-K certificates have prior art; the contribution hypothesis is this specialization and its demonstrated value.

## Complete results and interpretation

Independent B2/K10 stage (initial stage reported separately):

| Corpus | new n | Pair+enum | Best LP+enum | Discrete | Difference pp [95% CI] | p Holm (3) | Win/loss |
|---|---|---|---|---|---|---|---|
| scifact | 199 | 111 (55.78%) | 115 (57.79%) | 123 (61.81%) | +4.02 [+1.51, +7.04] | 0.015625 | 8/0 |
| nfcorpus | 223 | 37 (16.59%) | 41 (18.39%) | 45 (20.18%) | +1.79 [+0.45, +3.59] | 0.125 | 4/0 |
| fiqa | 548 | 67 (12.23%) | 71 (12.96%) | 91 (16.61%) | +3.65 [+2.19, +5.29] | 5.72205e-06 | 20/0 |

2 of the three independently preregistered dataset comparisons pass Holm-adjusted p<.05; this supports only the specified certificate comparison, not publication readiness.

Read the [Vietnamese report](REPORT_VI.md), [English manuscript draft](MANUSCRIPT.md), [theory](THEORY.md), [initial novelty audit](NOVELTY.md) and [expanded current related work](RELATED_WORK_UPDATE.md). The report includes zero-gain budgets, MILP wins, relevance-conditioned counts, numerical assumptions, a thread execution deviation and the limited isolated latency sample.

## Verify without raw data

From repository root:

```bash
pip install -r requirements-all.txt
python round3/verify_archive.py
python -m unittest discover -s round3 -p 'test_*.py'
```

Published evidence includes all selected per-query records (gzip), 27,000 individual sampled predictions, exact bootstrap draws, proof traces, 12 real-query fixtures, solver outcomes, plots, logs, source/ID freezes and checksums. All 300 primary rank profiles and budget-two adapters matched controlled full-corpus replay. These are implementation/statistical checks, not proof of every compiled library or of novelty.

## Run a new query on CPU

After downloading pinned data and building its local index as described in [REPRODUCE.md](REPRODUCE.md):

```bash
python round3/certify_query.py --dataset scifact --query 'vitamin deficiency affects bone growth' --budget 2 --k 10
```

No new labels, GPU, fitting or paid API is needed. The full corpora have 5,183/3,633/57,638 documents. Queries are limited to 32 normalized whitespace tokens; the guarantee covers only the declared finite per-token delete/swap/repeat/QWERTY model with worst-case ties. It does not certify semantic equivalence or relevance.

Cloud two-core/8 GiB execution completed these experiments. Local execution is optional for independent replication/more throughput; 16 GiB RAM gives useful margin. It does not increase language-model reasoning or automatically establish a contribution.

## Provenance

- Original source/300 IDs before metrics: [8dd7972](https://github.com/TruongTQ261531/N-Gram/commit/8dd7972dc13d85159e908f9b6ea03c394289acd2), [PROTOCOL_RETENTION.md](PROTOCOL_RETENTION.md).
- Independent source/970 fresh IDs/primary-result hashes before new metrics: [5fcf816](https://github.com/TruongTQ261531/N-Gram/commit/5fcf816da7d686427f518845c71e682d95626cee), [PROTOCOL_REPLICATION.md](PROTOCOL_REPLICATION.md). No stage pooling or significance-based stopping.
- Execution-only FiQA range adapter: [fb80e60](https://github.com/TruongTQ261531/N-Gram/commit/fb80e602df947ed12dc00d09c40e510f4e6cbe25), [EXECUTION_ADDENDUM.md](EXECUTION_ADDENDUM.md). Per-query source identity and final ID completeness checked.
- [RUN_HISTORY.md](RUN_HISTORY.md), [DATA_LICENSE.md](DATA_LICENSE.md), pinned `download_manifest.json` and `checksums.sha256`.

Raw corpus/query text, index pickles, literature full text and the uploaded Word file are excluded. Existing qrels evaluate original-query relevance only. No paper has been submitted, accepted or declared guaranteed Q1.
