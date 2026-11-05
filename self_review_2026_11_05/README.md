# Self-review continuation — 5 November 2026

Base commit: `d4b417f5354628a76007f59765a78e1d1ca0b043`. Local branch: `research/ipm-self-review-2026-11-05`. Read [SELF_REVIEW.md](SELF_REVIEW.md) for findings and their limits. No original algorithm, experiment freeze or result file is changed; manuscript files stay outside Git.

## Findings

All970 original contexts and full-prover rank bounds replay exactly. Holding the original pair/custom-LP/enum prefix fixed, equal-weight support gives250 certificates at B2K10 versus259 for full support/Pareto:9 full-only,0 support-only. Equal-weight support recovers23 of the32 original gains over Best LP. There is no false support certification among704 verified NONROBUST labels.

This is a retrospective **graph-component decision ablation**, not970 fresh LP/MILP runs and not an end-to-end timing comparison. Context construction and graph-only times exclude the reused prefix solver work. The earlier36-query20M-cell safeguard is not added here. Original120-check/80-candidate graph caps and every query remain.

First-fit can worsen under a stronger prover even without binding caps. Four combinatorial tests exercise the actual unchanged scheduler with64 abstract oracles, the uncapped counterexample,192 completed-graph edge additions and63 scaled separation instances. They do not refute the last-representative proposition, which concerns each scheduler's disclosed partial graph.

The equal-weight control is not an optimized linear separator. A fixed21-weight proof diagnostic on all285 positive Pareto checks in the32 original LP-gain cases recovers155 with outward linear supports. The other130 are inconclusive, not proof of impossibility for all weights. Of172 Pareto proofs within returned groups,76 remain unresolved by the grid;3 existing partitions are fully linearly recertifiable. The partitions were selected by the full prover; this does not give a new support-only scheduler, coverage result or matched cost.

Qrel-positive clean winners:311, with LP/Discrete/MILP coverage145/158/160. No-positive-judgment winners:659, with82/101/100. These are descriptive original-query strata, not relevance labels for edited queries. All original primary tests stay unchanged.

## Verification

From the repository root in the pinned scientific environment:

```bash
python -m self_review_2026_11_05.verify
python -m unittest self_review_2026_11_05.test_graph_review -v
```

The verifier is read-only and checks all IDs, frozen source hashes, replayed default bounds, safe graph groups, partial-graph last representatives, negative proof bounds, full label joins and the fixed-grid receipts. `logs/` contains successful re-execution of the original archive verifier and76 tests from9 relevant scientific directories in an isolated worktree, plus4 new tests. This does not mean every possible repository test or scientific objection was exhausted.

## Re-execution

Use a separate working copy, preserving this published `results/` elsewhere and creating an empty results directory. Restore the pinned raw distributions/indexes using inherited manifests. Raw scripts refuse to overwrite gzip receipts. No new network access is needed if the exact inputs are present.

```bash
python -m self_review_2026_11_05.replay --data "$DATA_ROOT"
python -m self_review_2026_11_05.linear_probe --data "$DATA_ROOT"
python -m self_review_2026_11_05.analyze
```

`FREEZE.json` is a local retrospective pre-run code/parameter freeze, not externally registered confirmation. `LINEAR_PROBE_SCOPE.json` separately freezes all32 selected original gain cases and21 weights before that diagnostic. The original model, channel and queries are unchanged. Generate a separate manifest for re-execution rather than expecting latency-bearing gzip bytes to equal the archived run.
