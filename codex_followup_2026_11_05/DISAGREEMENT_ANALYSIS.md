# Complete-cohort disagreement audit

All 970 IDs join successfully. LP=227, Discrete=259, later MILP=260; labels are 266 ROBUST/704 NONROBUST. All 32 Discrete gains over LP have successful generic LP solves. The union of LP/Discrete/MILP coverage disagreements has 34 queries. This is an all-case retrospective diagnostic, not outcome-based sampling of a new benchmark.

- NFCorpus PLAIN-2240: pair/LP/Discrete/MILP ranks 26/23/12/7.
- NFCorpus PLAIN-1141: 40/36/22/9.
- FiQA 5369: 24/19/8/13; numerical MILP time limit, reported gap 0.714286.

Both NFCorpus numerical MILP solves report optimal status; exact enumeration is resource-capped in all three disagreements. Neither caps nor LP failures explain away all opposing results. More complete pair construction in the existing retrospective refinement recovers the two NFCorpus cases, at the disclosed extra cost. The original method remains 259 vs 260. Graph checks, support/Pareto proof receipts, margins, alternatives and lengths accompany all cases in CSV/gzip traces.

LP-gain queries have median 12.5 retained tokens and 14 screened competitors, versus 9 and 120 in the remaining 938 queries. These are descriptive posthoc differences, confounded by difficulty and resource limits; they do not establish a causal length or margin effect. Only 13 gain winners have positive qrels.
