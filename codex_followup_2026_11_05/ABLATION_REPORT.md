# Retrospective 36-query component/budget panel

Selection: 12 per corpus, three hash-selected IDs per token-length quartile, without outcome-based filtering. FREEZE.json predates outcomes. This remains retrospective because the 970-query cohort and method behavior were already studied. All 684 pipelines finish; 20 return explicit context-cap unknowns. Original B=2 Best-LP and Discrete rank bounds match on all 36 cases.

At B=2,K=10: pair+enum 11/36; Best LP+enum 13; Discrete 15; support-only graph 14; Discrete without LP 15; without enumeration 15; MILP+enum 14. Custom-LP+enum alone also gives 13. Thus the graph has an incremental observed effect over LP and one full-Pareto/schedule gain over support-only. Neither LP nor feasible enumeration adds K=10 coverage after the graph on this small panel, although LP tightens 12 rank bounds and enumeration tightens one. Do not claim every component is necessary for the binary decision.

At B=2,K=20, support-only certifies 19 vs full Discrete 18. Pair-proof changes affect the resource-bounded first-fit/check schedule; a stronger pair oracle does not guarantee a stronger capped final cover. This adverse scheduling result is retained and the data do not support monotonic coverage dominance by the full Pareto layer.

At K=10 and B=1, all four principal methods certify 28/36. At B=3, pair/LP/Discrete/MILP certify 10/10/11/12, including three common context caps per method. This counterexample to uniform dominance is retained. Thresholding the same K-independent bounds at K=1,5,10,20 gives 2,736 decision rows, not four new timing runs. No new significance tests or confirmatory p-values are claimed.

Removing screening reaches the added context cap on 8/36 FiQA cases and certifies 13 vs 15. This shows a resource/completeness boundary; cap-shortened execution time is not a runtime advantage. See RUNTIME_ANALYSIS.md for sampled RSS and unmatched historical metrics. All per-query records and proof receipts remain available.
