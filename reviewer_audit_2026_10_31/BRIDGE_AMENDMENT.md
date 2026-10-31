# Additional backend checks after the first bridge pass

The first retrospective pass completed before this amendment: all6,684
observed top-k sets and128 unions agree, but the strict quantization-margin
rule proves only6,277 states. The407 unresolved states all have an integer
tie across the top-k boundary. Preserve that pass/source/output unchanged.

This SECONDARY post hoc check resolves close boundaries by exact dyadic sums
of stored float64 coefficients. It also constructs a casefold float index
on the same WANDS source/products and compact query lattice. The first pass
found5 product representations and0 raw queries whose lowercase/casefold
normalizations differ. Refit on the fixed corpus is necessary for this
separate normalization control; do not pretend it is the old index.

Use outward float dot-product enclosures to exclude documents far from a
decision boundary. For at most256 ambiguous documents, compare exact sums
using float.as_integer_ratio and Python integers/Fraction. Larger ambiguous
sets remain UNKNOWN. Zero reference scores are checked exactly; nonnegative
weights then imply worst-tie reference rank N. No boundary tie is broken
arbitrarily. Record both top-k unions and worst reference ranks/retention
decisions for the SAME designated clean reference and B=2 lattice.

This is a numerical-contract audit, not a new ranking method, a new test
set, a claim of identical scorers on all inputs, or independent validation.
Counts and scope above were known before the secondary calculations.
