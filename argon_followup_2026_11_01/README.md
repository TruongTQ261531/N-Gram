# Graph, neural and multiword follow-up audits

Retrospective extension of the existing research branch; original scientific
archives are unchanged. The manuscript and bibliography remain outside Git.

- [Full assessment in Vietnamese](RESPONSE_TO_ARGON_VI.md)
- [Methods, source rights and reproduction](README_VI.md)
- [Original protocol](PROTOCOL.md), [derived results](results/analysis.json)
- [Label-free optional refinement](refine.py), [query-schedule certificate](schedule_certificate.py)
- [Recovered original GTC provenance](GTC_SOURCE.json)

All 266 verified robust cases receive graph diagnostics. Complete pair proofs
plus standard DSATUR resolve the seven default-missed cases retrospectively.
Actual FP32 reranking covers 128 queries, 16 coarse-pool cost comparisons,
2,560 session requests and standard top50/top100 controls. Three separately
selected 200-pair multiword panels retain all failures and source distinctions.
These results do not establish global neural robustness, a new graph-coloring
algorithm, a newly collected corpus, global SOTA or Q1 acceptance.

```bash
python -m unittest argon_followup_2026_11_01.test_graph argon_followup_2026_11_01.test_multiword -v
python -m argon_followup_2026_11_01.check_archive
sha256sum --quiet -c argon_followup_2026_11_01/checksums.sha256
```
