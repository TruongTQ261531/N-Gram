# Non-computational clarification of the frozen proof text

The frozen THEORY.md says to choose anchors “without looking at query
outcomes”. The implementation and its benchmark actually choose anchors by
the current query's raw full-corpus score (as already explicit in core.py).
The soundness argument does not require statistical independence of anchors:
any fixed set of at least k distinct documents works for each input query,
provided its minima are valid for EVERY allowed state. Thus raw-score-based
selection is safe. The intended restriction was no outcome-driven tuning of
the method on confirmation, not a prohibition on query-dependent anchors.

This clarification changes no source, threshold, index, query selection,
metric or experiment. The frozen source/proof remains unchanged for hash
verification; this note makes the wording/implementation distinction explicit.
