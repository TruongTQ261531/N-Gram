# Closest work and claim boundaries — 1 November 2026 (Asia/Saigon)

This is a bounded primary-source review supporting the current claims. It is
not an exhaustive priority search or a certificate of Q1 acceptance. Source
content, bibliographic identity and execution of author code are different
types of evidence. `PRIMARY_SOURCES.json` records the inspected PDF bytes;
copyrighted PDFs remain outside Git.

| Work / inspected content | What is already established | Defensible distinction here / actual comparison |
|---|---|---|
| CostCert, Zhou et al.; arXiv2507.23335v1, Sections3.1–3.4, Eq1, Algorithm1, Theorems2–3. Published QRS DOI10.1109/QRS65678.2025.00030. The inspected text is the preprint, not an asserted identical publisher version. | Pairwise attack-budget inflation; one shared mutable atomic-vote budget; minimum extra tie cost; unfavorable reference ties. | Finite token alternatives give correlated **vectors** of document-score changes. The bundled-vote fixture isolates attainable choices versus free allocation. It is a mathematical specialization checked against brute force, not CostCert author-code execution, a fixed-BM25 realization proof, or evidence that every CostCert adaptation is weaker. |
| Mouratidis and Tang, PVLDB2018, DOI10.14778/3204028.3204031; Section3.1, Section4 Definitions1–2 and filtering/refinement, Section5 JAA. | The exact possible-top-k union, regional dominance, dominance graphs and partition verification over a continuous preference region. | One-hot finite alternatives plus a shared changed-position budget are an explicit discrete domain. Convexification can add winners; this does **not** make UTK unadaptable. Original-attributed mirror code was executed on a conformance fixture and128 NLP segments, of which121 had exact segment oracles and7 hit the oracle cap. Neither a complete finite-lattice RSA/JAA adaptation nor a valid matched full-workload runtime comparison was executed. Native disagreements are implementation diagnostics, not a refutation of the paper. |
| Wong and Kolter, ICML/PMLR80,2018; Section2, Section3.1 Eqs2–4 and Section3.2 Theorem1. Primary proceedings PDF. | Convex outer bounds, LP margin verification and feasible dual bounds; Section2 explicitly discusses exact SMT/integer and combinatorial verification. | Our additive finite-domain support problem and top-K competitor count are different instances. The separation proves a gap for the **specified matched relaxation**, not a general superiority theorem over convex verification, disjunctive branch-and-bound, cutting planes or exact solvers. The paper's neural algorithm was not executed as a lexical baseline. |
| Bast and Celikik, Efficient Fuzzy Search in Large Text Collections, TOIS2013; author manuscript abstract, Section2.2 Definitions2.3–2.5, Section3 filtering discussion. Publisher DOI10.1145/2457465.2457470. | Error-tolerant dictionary/full-text search, inverted-index preprocessing and candidate filtering are established. | A fixed additive-ranker retention bound and its exact finite-state result union are the declared targets here. Index-first safe filtering is a specialization; no generic firstness or direct performance comparison with CompleteSearch is asserted. The author PDF has placeholder journal/DOI fields: use verified publisher metadata, never those placeholders. |
| Zhao, CertEx; arXiv2610.21325v3,27Oct2026, Section3 exclusion proposition, lifted lower bound and numerical certificate. Explicitly a preprint. | Safe exclusion before exact verification, low-precision bounds and rounding-error accounting for fixed-query Euclidean kNN. | Finite query variation and additive lexical output contracts differ from its vector-search task. No H100/GPU or mixed-precision speed comparison was run. Conservative pruning and numerical error bounds are not claimed as inventions here. |

## Explicit mapping to established discrete verification

Let x_ia be a one-hot token-alternative choice, sum_a x_ia=1 and
sum_i(1-x_i0)<=B. Each margin is linear in x. A binary z_j indicating a
nonnegative margin yields a conventional mixed-integer cardinality model
(with valid big-M or indicator constraints). If two competitors cannot be
nonnegative together on this domain, z_j+z_l<=1 is a standard conflict cut;
a conflict clique implies sum z_j<=1. A clique cover therefore bounds the
number of jointly promoted competitors. Pareto dynamic programming and
DSATUR are established algorithms. This mapping identifies close prior
machinery; a new input domain, a new name or the LP-gap example alone cannot
establish an algorithmically new general verifier.

Executed matched controls are the existing custom/generic LP+enumeration,
numerical MILP+enumeration, wider exact enclosure enumeration and the
recorded resource profiles. Their caps, unknowns and negative comparisons
remain visible. MILP numeric dual bounds are solver references rather than
formally interval-validated proofs. No separate general disjunctive verifier
was implemented this turn. The all970 replay evaluates the **unchanged**
existing full-pair/DSATUR refinement; it adds validation, not a new method.

## Claim ledger for the manuscript

| Claim | Evidence and permissible wording | Excluded extrapolation |
|---|---|---|
| Central method | A resource-bounded finite-query retention certifier, with identified arithmetic assumptions, incompatibility proofs and an explicit cover bound. | First shared-budget top-K certificate; new LP/Pareto/DSATUR theory; unconditional formal verification of numerical libraries. |
| Coverage | Original locked970:Discrete259,BestLP227,MILP260;266 robust and704 nonrobust under the later decision audit. Two of three LP comparisons pass original Holm-adjusted tests. | Discrete uniformly beats MILP; replace original counts/tests using later refinement. |
| Existing refinement | Report all970 label-free routes, total cost and false certifications against the post-run label join. | Oracle-selected seven-case success presented as an unseen all-query result; general exact worst-rank claim. |
| Exact union application | All128 WANDS unions match full enumeration;2.3474x geometric construction ratio against the faster executed matched offline control. | 2.35x interactive/cross-encoder/RAG speed; faster than original RSA/JAA. |
| Numerical coherence | Same structural factors/output questions, explicitly distinct original backends/channels; matched bridge finds real state/rank mismatches despite union and decision agreement here. | One numerically identical end-to-end ranker; transfer of compact-integer speed/full-float-channel coverage. |
| Channel scope | Mitton55/100;JFLEG human11/200;JFLEG Enchant55/200;GTC91/200 atB2. | 91% natural-query coverage; human semantic gold; a new dataset. |
| Cascade transfer | Same per-state lexical inputs imply the same fixed cascade inputs; matched memo controls both need67571 distinct pairs across6684states. | Global neural top10 preservation, fewer neural inputs, edit-invariant neural ordering or answer robustness. |
| Practical boundaries | Original session gate fails; coarse-to-union neural top10 mean containment65%;ordinary raw top50 is cheaper/slightly higher nDCG in its diagnostic. | Hide failed gates in appendices or call static clean-pool failure ordinary per-query retrieval failure. |

The organizing question is: **which outputs of a fixed lexical ranker can be
certified under a shared finite query-edit budget, and at what cost?**
Retention and possible-result union are two output contracts, with different
tie rules, rather than four separate novelty claims. Correction corpora and
neural controls measure scope and transfer. They are not sequential modules
of an evaluated end-to-end system. Fig1/Fig2 remain undrawn placeholders.
