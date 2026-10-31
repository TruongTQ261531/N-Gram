# Exact decisions, resource profiles and spelling-type pilot

This supplement is retrospective. All original freezes, method outputs,
query IDs and numerical indexes remain unchanged. Manuscript files and raw
pilot text remain outside Git. Figures are not drawn.

## Completed evidence

- All970 fixed B2/K10 decisions resolved:266 robust,704 nonrobust,0unknown.
- Negative decisions have exact dyadic stored-weight witnesses, including
  unfavorable ties; positive decisions use exhaustive upper enclosures with
  frozen screening/IEEE assumptions. This is not compiled-library formal
  verification or exact worst-rank computation.
- Original BestLP/Discrete/MILP coverage remains227/259/260. Discrete covers
  259/266 robust queries and closes32/39 of the verified LP gap (82.05%).
- Six frozen resource profiles on144 fixed prior queries:864 executions.
- Matched larger-cap enumeration versus default on the same panel:288 executions.
- All8 robust default-boundary cases tested,56 executions: extendedDiscrete7/8,
  MILP5s8/8,wide-enumeration8/8. These cases are outcome-selected diagnostics.
- Author-curated Wikipedia misspelling pilot:100 preselected types,55 covered,
  Wilson95 [45.24%,64.39%],B1=B2. Not query traffic or semantic labels.

The new panel was measured on an Intel Xeon Platinum8573C host; older all970
measurements used AMD EPYC9V74. Compare costs only within matched blocks.
The profiles are independent resource settings, not a continuous anytime trace.
Default Discrete already covers all25/8/9 robust queries present in the
fixed panel, so flat curves do not establish global budget sufficiency.

The wider enumeration control has the same panel coverage as Discrete;
its paired geometric cost ratios enum/discrete are1.59/1.38/1.47 across
SciFact/NFCorpus/FiQA. These are retrospective descriptors, not new primary
speed tests or universal superiority claims. Wider budgets recover original
misses, as the separate boundary diagnostic explicitly shows.

## Pilot source amendment

The author-linked GTC bucket no longer exists. The located community mirror
lacks verifiable original language/typo-label provenance, so it was not used.
TYPO_SOURCE_AMENDMENT.md documents the
switch before membership outcomes to Roger Mitton's institution-hosted
Wikipedia misspelling list. Its curation/lexicon filters and type-level
sampling restrict interpretation. No raw corpus text is redistributed.
Source bytes/documentation hashes and selected pair hashes are supplied.

## Reproduction

Use pinned round3/requirements.txt dependencies and external original-data
caches. Read PROTOCOL.md and all *_AMENDMENT.md files, plus the source
hashes/IDs in the five *_FREEZE.json files.

```sh
python -m unittest discover -s decision_audit_2026_10_31 -p 'test_*.py' -v
python -m decision_audit_2026_10_31.check_archive
sha256sum --quiet -c decision_audit_2026_10_31/checksums.sha256
python -m decision_audit_2026_10_31.analyze --runs decision_audit_2026_10_31/results/budgets --wide-runs decision_audit_2026_10_31/results/wide_enum --decisions decision_audit_2026_10_31/results/decisions.json.gz --output /tmp/decision-analysis.json
```

The boundary input defaults to the released boundary.json; use --boundary
to analyze another explicitly chosen record. For full numerical reruns, use module CLIs decisions,budgets,wide_enum,boundary,typos with a
new output path; outputs reject overwrite. Time datasets sequentially with
no competing benchmark/compilation. Do not pool repeats or selected stress
cases as independent new queries.

## Scientific boundary

The work strengthens evidence about the declared certifier and fixed
benchmark. It does not establish global SOTA, new human relevance data,
end-to-end RAG safety, neural inference savings, or guaranteed Q1 readiness.
RSA/JAA remain a native conformance fixture rather than a matched NLP
performance control. Contract examples do not establish algorithmic priority.
