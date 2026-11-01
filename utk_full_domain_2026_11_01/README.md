# Full finite-domain UTK control completion

Retrospective completion of the matched offline-union comparison requested
on 1 November 2026. See [the Vietnamese report](REPORT_VI.md),
[protocol](PROTOCOL.md), [pre-run freeze](FREEZE.json),
[paper-to-code mapping](METHOD_MAPPING.md) and [complete analysis](results/analysis.json).

The workload is **all 128 original WANDS queries, all 42,994 products and
all 6,684 admissible correlated states**, with the unchanged integer scorer,
compact channel, full queries, B=2, k=10 and all kth-score ties. No selected
score segment or convex box substitutes for the complete finite domain.

Two independently written baseline adapters implement regional dominance
and RSA's candidate-specific verification or JAA's shared anchor arrangement.
They are named **RSA-FD/JAA-FD** to distinguish them from the original
continuous-region C++ programs. State cells replace continuous geometry,
pivot scanning replaces R-tree traversal, strict regional dominance and
explicit equality cells preserve the tie-inclusive target, and complete
anchor comparisons replace incremental half-space insertion. See the mapping
for implemented and omitted optimizations. This is baseline completion,
not a new claimed contribution or native-C++ performance reproduction.

The default three-repeat study completes RSA-FD/JAA-FD on126/127 of128
queries. A separately frozen all-query first-pass profile removes the
arrangement-node cap while retaining the common120-second wall guard:
both adapters complete127/128, with query170 returning resource_unknown.
All exact outputs match full-corpus replay. The source audit checks8,298,930
strict-dominance minima. See [the supplemental protocol](RESOURCE_PROFILE.md)
and [profile results](results/profile-analysis.json); these do not replace
the default measurements. There are48 passing unit tests in total.

Compare the adapters against unchanged screen+batch and parent controls.
All methods independently incur their whole pipeline cost and share only
the immutable warm index. Retain three executions per query with hash-rotated
method order, one numerical thread, all caps/errors and the full query
denominator. A safe resource-unknown superset never counts as exact.
Only completed same-target pairs support descriptive cost ratios; all-query
cost distributions separately retain resources spent on unknowns.

After timing, complete-text sparse scoring of the original full corpus
independently checks every state, every exact union, RSA witnesses and JAA
cells. A further source audit checks strict dominance minima and screen
receipts against all-state full-corpus scores. It does not merely compare
the final union with an earlier selected sample. All old protocols, original
primary tests, failed session results and neural limitations are retained.

## Inspect or verify the release

With the repository's pinned numerical requirements installed:

```bash
python -m unittest utk_full_domain_2026_11_01.test_algorithms utk_full_domain_2026_11_01.test_archive -v
python -m utk_full_domain_2026_11_01.check_archive
sha256sum --quiet -c utk_full_domain_2026_11_01/checksums.sha256
```

Large execution gzip bytes are split into parts below ordinary Git file-size
limits. `archive.py` checks each part and the exact concatenated hash before
decompression. Analysis/verification reads the parts directly, so manual
reassembly is unnecessary. No numerical measurement is changed by splitting.

`results/per_query.csv` contains one median per query/method, not independent
rows for timing repeats. `records.parts.json` identifies the exact execution
archive; `oracle.jsonl.gz` records every full-corpus top-k state;
`source_audit.json` records independent dominance/screen validation.

To rerun timings, restore the original byte-verified WANDS data and index
following the earlier study instructions, then use a fresh output directory:

```bash
python -m utk_full_domain_2026_11_01.run --data /path/to/wands --output /path/to/fresh-results
```

The runner refuses an existing output directory and checks source/code/index
hashes. The release's replay, source-audit and analysis entry points validate
the recorded release paths; keep new runs separate and compare their exact
unions with the published all-state oracle. Reproducing full source audits
requires the original private data/index, not just the public numeric receipts.
The archive checker does not independently revalidate unavailable raw data.

Our implementation uses the repository code license. WANDS lineage/terms
remain documented in the original study. Raw queries/products, indexes,
third-party source/binaries and copyrighted PDFs are not added to Git.
Manuscript `main.tex`/`references.bib` stay outside GitHub; Fig1/Fig2 remain
undrawn placeholders. No Q1 acceptance, global priority, original-C++ speed
or unrestricted natural-error/neural robustness is asserted.
