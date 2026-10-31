# Verification-only addendum

Written during the supplementary FiQA timing run on31October2026, before
executing this verifier. All additions remain retrospective. The original
method, inputs, query selection, caps, first-pass bounds and timings are
unchanged. Nothing here defines a new primary outcome or confirmation set.

After all970 first-pass records complete, select EVERY query whose K10
coverage decision differs among BestLP+enum, Discrete, MILP+enum. Selection
includes differences favoring either method. Run exhaustive upward-rounded
margin enumeration on the same frozen screened competitors, with caps of
2million states and500million state-candidate cells. Record unknown when
a cap is exceeded. A maximizer of an upper enclosure is not an attack
witness. This verifies rank upper enclosures; it does not independently
re-prove shared screening or the sparse numerical error model. A verified
positive can support a reported certificate; an inconclusive upper bound
does not refute a MILP result. Larger verification caps never enter the
competitive table or replace its reported ranks/times.

Record all three method ranks, fixed query/model identities, enumerated
state counts, outcomes and cap failures. Preserve output without silent
overwrite. Validate the vectorized enumeration against the original scalar
operation order and resource-unknown behavior before running corpus cases.

The descriptive analyzer also reports pre-specified paired timing ratios,
first-pass method positions and repeat stability. Its2000-draw bootstrap
intervals are retrospective summaries, not an additional primary speed test.
Repeat coverage changes remain visible and never select the reported pass.

Native UTK testing is a separate exact three-record continuous-region
fixture, not a large corpus or NLP timing benchmark. Preserve both an
IO-only upstream build and a variant correcting the epoch-bound guard.
Source/binary hashes distinguish them. Do not redistribute third-party
sources/binaries or interpret an implementation failure as a refutation of
the paper's mathematical algorithms.
