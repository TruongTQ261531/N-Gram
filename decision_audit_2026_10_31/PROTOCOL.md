# Retrospective decision, budget and observed-edit supplement

31 October2026, Asia/Saigon. Earlier query outcomes are known. This is
retrospective verification and diagnostics, not independent confirmation.
Use the existing research branch. Preserve all frozen source/results.
Manuscript TeX/BibTeX stays outside Git; Fig1/Fig2 artwork stays pending.

## Decision verification

Use every original199/223/548 replication ID, B2/K10 and original source/
model hashes. Start with the observed partition261 certified,693 strict
point-score witness cases,11 zero-reference and5 unresolved. Reconstruct
states from archived support/MILP records (including repeats), raw state
and saved zero-reference choices. Check variant membership and token cost.
For a violating state, evaluate stored float64 weights as exact dyadic
rationals with integer query counts. At least10 other documents scoring
at least the fixed reference prove unfavorable rank>10. Floating scores
only select documents to examine; they are never the proof of violation.
An exactly zero reference plus the checked nonnegative index proves rank N.
Verify text-feature counts equal the sum of selected token-state counts.

Cross-check all261 positive decisions with the existing larger-cap
exhaustive upper enclosure (2million states,500million cells). Keep cap/
boundary unknowns explicit. This positive audit shares frozen screening
and the original sparse error model, unlike the exact selected-document
negative comparisons. No compiled-library formal verification is claimed.

For remaining undecided cases, enumerate when within the above caps and
check the enclosure maximizer as a candidate witness. Then allow10second
and, if needed,30second MILP witness search on these cases only. Solver
bounds alone never supply new oracle labels: require exact witnesses or
the exhaustive upper enclosure. Never change original method coverage/time.

## Budget profiles

Use the SAME48 fixed timing-panel IDs per corpus in reviewer scope.json:
144 previously observed queries, no outcome-based resampling. Numerical
threads1, warm immutable index, query/screen/materialization included,
one pass with SHA256-rotated six-profile order, dataset jobs sequential,
no competing study benchmark or compilation during measurement.

MILP solver limits0.1,1,5seconds, fixed2million matrix-entry and original
enumeration caps. Discrete profiles use (LP cuts,pair checks)=(10,30),
(40,120),(160,480); all use80 graph candidates and original Pareto/
enumeration caps. The default discrete profile must replay frozen ranks.
These are independent resource-setting runs, NOT a continuous anytime
trace. Do not enforce monotonicity by selecting favorable runs for free.
Report coverage, full-pipeline median/IQR/P95, solver statuses, finite dual
bounds and coverage/runtime data in CSV. No figure artwork is drawn yet.
All profiles include all panel queries and remain retrospective diagnostics.

## Repository-derived correction pilot

GitHub Typo Corpus v1.0.0, official author repository/download. Pin source
revision and downloaded bytes. Select100 distinct raw(src,tgt) pairs by
smallest SHA256(seed|src|tgt), seed20261031, from pairs with both language
labels eng,is_typo=true, unequal raw text and max512codepoints per side.
This is an automatic dataset-label/length filter, never an A_B membership
filter. Count all eligible/duplicate/excluded records before sampling.

Treat corrected tgt as clean and erroneous src as perturbed. Normalize
with the frozen NFC/casefold/whitespace function; use the frozen generator
and exact minimum token-position edit cost, including empty alternatives.
Report no-op normalization separately, >32-token input-scope cases and
out-of-channel cases, coverage B1/B2 and Wilson95 intervals. No token
insertion/merge/2changes-in-one-token is admitted by assuming distance<=2.
Do not claim natural search-query traffic or semantic-equivalence labels.
Raw text stays outside Git because upstream texts retain per-repository
terms. Publish pair hashes/identifiers, selection provenance and aggregates.
