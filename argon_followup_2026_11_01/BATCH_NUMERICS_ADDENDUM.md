# Batch-dependent numerical implementation

Before the complete INT8 cross-pool metrics: dynamic quantization can use
activation scales depending on batch contents. Therefore do NOT assume a
common pair receives exactly the same logit in U-only and P batches. Retain
overlap-score discrepancies for both repetitions. Report top10(P) containment
in U as a property of that recorded P execution, not numerical equivalence of
different batches. Do not attribute all ranking differences solely to U pruning.

The matched cascade controls produce the same ordered lexical candidate
inputs; they can use identical batches and the same identical-pair memo cache.
Their input-identity proof does not transfer neural logits across DIFFERENT
requests or batches. The PyTorch FP32 partial cost block is separately retained
as an unquantized cross-pool diagnostic; never pool its timing with INT8.
