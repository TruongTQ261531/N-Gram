# Consolidating current claims

This supplement addresses three tasks requested on1November2026:

1. Organize the local manuscript around certifiable outputs of a fixed
   lexical ranker under a shared finite query-edit budget. Retention is the
   central method; exact union is a complementary audit application.
   Correction/neural studies delimit scope and transfer. Lengthy diagnostics
   move to appendices with all prior scientific tables and proofs preserved.
2. Review closest primary sources and distinguish established machinery,
   contract differences, actually executed controls and unresolved comparisons.
   See [the audit and claim ledger](CLOSEST_WORK_AUDIT.md) and
   [inspected source identities](PRIMARY_SOURCES.json).
3. Replay the **existing** full-pair+DSATUR refinement on all original970
   B2/K10 query IDs without loading outcome labels in the runner. Record
   costs on robust and nonrobust queries, routing/caps, proof groups and
   post-run decision agreement. This is retrospective validation, not an
   additional method or an unseen confirmation.

No new algorithm, model, corpus, error channel or novelty-development
experiment is introduced. Original scientific releases and comparisons
remain unchanged. `main.tex`, `references.bib`, figures and all manuscript
files stay outside this Git repository. Fig1/Fig2 remain undrawn placeholders.

## Recorded results and scope

See [the complete analysis](results/analysis.json),
[run metadata](results/metadata.json), [protocol](PROTOCOL.md),
[pre-run ID/source freeze](FREEZE.json), and [Vietnamese report](REPORT_VI.md).
Per-query compressed records contain hashes/IDs, bounds, routes, conservative
pair proofs, cover groups and integrated timings; no raw corpora or private
indexes are redistributed.

Original locked results remain Discrete259,BestLP227,MILP260, with266 robust
and704 nonrobust labels in the later decision audit. The new replay is
reported separately and cannot replace original hypothesis tests. Integrated
prefix/additional/total times are components of one run, not independent
randomized two-method speed measurements. Shared warm-index loading is
excluded. Numerical assumptions and the existing120-second construction
guard/80-candidate cap remain explicit.

## Reproduce/check

From the repository root, using the numerical versions in the run metadata:

```bash
python -m unittest claims_consolidation_2026_11_01.test_routing -v
python -m claims_consolidation_2026_11_01.check_archive
sha256sum --quiet -c claims_consolidation_2026_11_01/checksums.sha256
```

To rerun the benchmark, first restore the original byte-verified corpus/index
inputs using `reviewer_audit_2026_10_31.restore_data` and the existing
reproduction instructions. Do not overwrite this release's result files:

```bash
python -m claims_consolidation_2026_11_01.run \
  --data /path/to/restored-data --output /path/to/fresh-run
```

Run datasets sequentially without another benchmark. The runner fixes one
numerical thread and refuses an existing output directory. The release
analyzer joins the prior decision archive **after** the run. Archive checks
recompute summaries and validate every recorded cover against the logged
conservative pair proofs; these are consistency checks rather than a new
independent validation of the entire sparse/numerical software stack.

The code uses the repository's existing license. Query IDs and derived
numerical audit records retain the source lineage and restrictions documented
in the earlier retention artifacts. Primary PDFs, raw text, corpora, weights
and indexes remain private/outside Git; no additional data redistribution is
introduced by this supplement. No Q1 acceptance or global SOTA is asserted.
