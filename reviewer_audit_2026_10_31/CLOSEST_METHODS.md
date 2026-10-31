# Closest-method contract audit

Retrospective analysis prompted by reviewer criticism. This document does
not establish algorithmic priority, global SOTA, or Q1 readiness.

## CostCert

Primary source: Zhou et al., arXiv2507.23335v1, Sections3.1–3.4,
Eq1 and Theorems2–3. The primary PDF was retrieved after network recovery.
CostCert already corrects inflated pairwise attack budgets: given a patch
region, unaffected mutants provide fixed clean votes; affected votes form
one shared atomic budget. It finds the smallest tie cost for promoting
enough competitor labels. Its target uses unfavorable ties. Those ideas
cannot be claimed as new merely because our input is a query.

`contract_checks.free_vote_worst_rank` is a mathematical single-region
specialization of that condition, checked against brute-force allocations.
It is NOT execution of the author software or a neural patch experiment.

Consider M competitors, one fixed clean vote for the reference, and M
mutable votes. Independent allocation can put one vote on each competitor,
producing unfavorable reference rank M+1. If one admissible shared choice
instead moves the ENTIRE bundle to a single competitor (or keeps it on the
reference), attainable worst rank is2. This fixture distinguishes the free
allocation relaxation from a correlated finite state set. It does not
refute soundness on CostCert's declared model, demonstrate a new general
conflict-graph theorem, or establish realizability by our fixed BM25 index.
A stronger closest-method comparison remains necessary.

## UTK: RSA/JAA

Primary source: Mouratidis and Tang, PVLDB11(8),866–879,2018,
DOI10.14778/3204028.3204031. RSA computes possible top-k options over a
continuous region of preference weights; JAA additionally partitions that
region into cells with a constant top-k outcome. The union target,
regional dominance and partition reasoning therefore predate this project.

A finite alternative tuple embeds as one-hot feature weights with a shared
edit budget. Replacing those tuples by a convex region can add winners:
for records(1,0,0),(0,1,1),(5/8,5/8,5/8), k1 and weights
w1 in[1/4,3/4],w2 in[1/20,1/10],w3=1-w1-w2, the continuous union
is{1,2,3}; the two allowed endpoint states w1 in{1/4,3/4},w2=3/40
have union{1,2}. The third record is a strict winner at w1=1/2, so the
counterexample does not depend on numerical boundary ties.

An author-attributed source mirror self-identifies via the exact DOI:
https://github.com/cupermanrose/UTK_source at
16466c87b08e2e368ba870cdcbbf31dc36be406b. Its README restricts
redistribution. Source/binaries remain outside this repository. Attribution
in a mirror is not independent authentication by the paper authors.

The native executable requires a documented IO harness: read the requested
region rather than generate50 random regions; export option IDs. Preserve
algorithm-source hashes and all failures. On the initial three-record
fixture, RSA returns1,2,3 but upstream JAA returns only3. An epoch overflow
guard compares positive values against `2 >> 31` (zero), discarding queued
subregions. Any explicit-bound correction must be a separate labeled
variant, with its result kept alongside the upstream failure. Do not infer
that the published JAA algorithm is mathematically incorrect from this
implementation issue. `native_utk.py` records repeatable fixture inputs,
private source/binary hashes and native outputs.

This conformance fixture does not close the matched NLP comparison gap.
A convincing future control could adapt original regional pruning to the
correlated lattice and retain exact finite membership, or combine a safe
continuous-domain candidate superset with exact finite verification. Keep
adaptation cost and tie/numerical assumptions visible. Merely substituting
a convex answer for the exact finite union, or renaming our existing
batch/parent control RSA/JAA, is not acceptable.

## Matched controls already available

Best custom/generic LP+enumeration and numerical MILP+enumeration use the
same discrete variables, edit budget, source scorer and query IDs. MILP
uses a1second solver limit and2million-entry cap, with whole-pipeline cost
measured separately from its solver limit. Its numerical dual bound is not
formally interval-validated. Keep all cap/timeout/fallback outcomes and
first-pass results; repetitions do not authorize choosing favorable bounds.

The reviewer supplement restores the exact original bytes/index hashes and
measures these controls on all970 retained query IDs. Complete logs and
current analysis, rather than this narrative, determine final counts.
These are retrospective same-query additions, not new independent queries.

## Recent exact-search boundary

The bounded arXiv title screen through31October2026 located Zhao, CertEx,
arXiv2610.21325v3. Primary metadata and the PDF were retrieved. Its safe
low-precision lower-bound projection and exact survivor verification target
fixed-query Euclidean kNN rather than a whole correlated query lattice.
This reinforces the existing disclaimer: safe exclusion and rounding-aware
filtering are not general firsts of our method. This is scope inspection,
not execution of its GPU implementation or an exhaustive prior-art screen.
