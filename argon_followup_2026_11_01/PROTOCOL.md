# Retrospective tests of Argon proposals 2–4 — 1 November 2026

Parent d026330; same research branch. No earlier files/results are replaced.
LaTeX remains outside Git. No main merge or website deployment. Source/model
acquisition is permitted before outcomes; selection rules below precede metrics.

## 2. Exact graph analysis

All 266 verified robust B2/K10 replication cases, unchanged scorer, 32-token
retention scope. Replay the original capped (120 checks, <=80 candidates)
incompatibility graph. Compare original greedy clique cover, exact coloring of
its complement and exact maximum compatible clique. These are DIFFERENT bounds:
chi(H) >= omega(H); a color-cover gap alone does not prove higher-order constraints
are needed. Integer bitset algorithms, 5 seconds/search, return feasible safe
upper bounds/explicit unknown if not proven optimal. No guessed exactness.

On ALL seven robust cases missed by default Discrete, additionally check every
candidate pair with unchanged outward Pareto/support proofs. Cap construction
at 120 seconds/query; retain all checks and unknowns. Run both exact searches on
the stronger graph. An absent certified conflict is not proof of compatibility.
Do not infer that a higher-order constraint is logically necessary from capped
or outward-ambiguous pair tests. Graph counts are retrospective diagnostics, not
new confirmation or global method originality.

## 3. Actual cross-encoder inference

Pinned cross-encoder/ms-marco-MiniLM-L-6-v2 (HF revision in source manifest),
torch2.8.0+cpu/transformers4.57.1; eval/inference mode, four CPU threads, float32,
batch32, fixed padding/truncation length256. No model training or tuning on
outcomes. Same WANDS products/queries/grades and 128 locked confirmation IDs.
Record model hashes, token truncation, number of pairs, warmup and wall time.

All128 raw queries: score their exact lexical union U with the neural model.
Report graded relevance coverage (grades>=1 and grade2 separately), including
unjudged status, without equating lexical containment to global neural recall.
On16 IDs with smallest SHA256(argon-ce-cost-v1|id), additionally score the
same raw query against the coarse pool P. Both endpoints use SAME model,
preprocessing and document text. Two measured executions in alternating order,
full tokenization+inference+ranking, no result caching between runs. Check
overlapping pair scores and whether neural top10(P) lies in U. This is a raw-query
candidate-restriction diagnostic, not a certified global neural top-k result.
The corpus-wide-neural baseline is not mandatory work for a lexical cascade.

All128 frozen 20-request sessions: construct per-request lexical top10 with all
ties on full corpus and on the stored U; require identical answers. Score those
actual query/document pairs, memoized ONLY on identical (request text,doc) pairs.
The same cache rule applies to both lexical controls. Compare pair identities
and counts; never cache neural scores across different queries. Record actual
inference time once on this identical pair trace, not a fabricated speedup from
scoring all U instead of ten. Do not claim production/end-to-end acceleration
from component measurements or reuse older-host timing numbers.

Predeclared 90-minute wall cap for neural measurements; retain partial results
and all planned/unmeasured IDs. CPU-only capability is a measured limitation,
not evidence against GPU performance. No neural and graph benchmarks run together.

## 4. Multiword correction pilots

GTC author bucket is unavailable and the sole located mirror lacks source labels.
Do not silently treat the mirror as the original corpus. Use author-hosted JFLEG
commit ee06ff806a208aba815ac45313f4e750a48330a5, dev+test, as explicitly different
multiword proxies. Two panels, up to200 unique nontrivial pairs each:
(a) raw source vs human ref0 (general learner-English grammatical/fluency
corrections, NOT spelling-only); (b) raw source vs authors' Enchant-spellchecked
source (automatic preprocessing targets, NOT human gold corrections).

Clean target -> erroneous source direction. Each side >=2 normalized tokens,
unequal after unchanged NFC/casefold normalization, <=2048 codepoints. No filter
on edit distance, number of changed tokens, channel membership, B1/B2 acceptance
or favorable references. Deduplicate within each panel; select smallest
SHA256(argon-multiword-v1|panel|source\0target). Save selected hashes/line IDs
BEFORE membership evaluation. Keep >32-clean-token cases as outside scope.
Use exact unchanged token-form generator and min-cost DP (including empty forms).
Report B1, B2, increments, structure/operation categories and source restrictions.
Panels may overlap; never treat them as independent population replications.
No raw texts redistributed; preserve author attribution and CC BY-NC-SA4.0 terms.

## Interpretation

All three directions are tests, not promises of improved results. Exact coloring
and neural models do not establish global novelty. More realistic data need not
give Argon's predicted coverage. Any protocol amendments precede their dependent
outcomes and are retained separately. This work cannot guarantee Q1 acceptance.
