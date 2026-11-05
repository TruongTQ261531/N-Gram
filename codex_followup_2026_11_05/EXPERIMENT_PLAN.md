# Frozen follow-up plan — 5 November 2026

This is retrospective validation of existing claims, not new confirmation and not a new ranking model. The 970-query primary freeze and every old artifact remain unchanged. Source: origin/main `63ceeda350a0f7e3c9138c3b1232d2ea06e49054`.

## Reuse instead of recomputation
Join all 970 primary rows with the archived three-method runtime audit, later MILP audit, and 266/704 decision audit. Clean-query metadata are replayed from pinned inputs; no solver outcome is used to select the new sample. Missing historical stage-memory metrics remain missing.

## New matched panel
36 queries: 12 per corpus, three hash-selected IDs per within-corpus token-length quartile. Selection and code hashes are in FREEZE.json. On B=2 run 11 configurations; on B=1 and B=3 run pair+enum, best LP+enum, Discrete, MILP+enum: 684 fresh full-pipeline executions. Threshold each K-independent rank bound at K=1,5,10,20. Shared immutable warm index; fresh context per method; one thread; one pass; deterministic hash ordering. Timings are exploratory and do not replace the full-970 controlled audit.

All original graph (120 checks/80 candidates), exact-enumeration (2,000 states/2M cells), LP (40 iterations/2M generic entries) and numerical MILP (1 second) caps remain. A common new 20M dense-score-cell cap protects this bounded follow-up; capped queries return full-corpus rank/unknown and remain in denominators. A 75 minute overall wall limit retains partial records. RSS is sampled every 20ms including the resident index; this is a sampled process peak, not exact method-local memory. Cumulative process HWM is separately labeled. Compare original B=2 LP/Discrete bounds to the freeze; any unexplained mismatch blocks interpretation. MILP time-limit variation is reported, never cherry-picked.

## Independent small-domain check
Enumerate complete small query domains using manual n-gram counts and exact dyadic integer arithmetic over stored float64 weights. Include repeated tokens, ties, OOV, empty deletions and stable winners. Do not reuse the certifier DP or graph for the oracle. Any certified rank bound below the exact worst rank is a failure and must be retained. These small domains do not establish new full-corpus ground truth.

## Reporting
Report disagreements and negative ablations; no significance claims from 12-query corpus panels. Preserve the failed session gate and neural containment/relevance limits. No reserved Fig1/Fig2 artwork is produced. Manuscript files remain outside Git.
