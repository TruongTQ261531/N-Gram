# Final CPU implementation: original FP32 weights, length-bucketed batches

Fixed256 padding wastes CPU work on short documents in both FP32 and INT8
attempts. Preserve completed INT8 records as a separately labeled numerical
diagnostic and interruption receipt. No partial cross-backend timings are pooled.

For the complete experiment, use original pinned ONNX FP32 weights with the
standard reranker implementation improvement of sorting pairs by encoded length,
batching32, padding each batch to its longest sequence, then restoring original
pair order. Keep the SAME maximum256-token window, actual unpadded token IDs,
model, all128queries,16costIDs,two repetitions,threads,cache rules and90-minute
cap. Apply this equally to U and P. Sorting/tokenization/padding are included in
the measured time. This is an implementation/resource amendment, not tuning
the input window, query selection, quality labels or model against outcomes.

No quantization is used in these complete measurements. Complete the all128 raw-U
PyTorch FP32 fixed-padding reference as already specified; report numerical
differences and rank agreement rather than assuming bitwise identity. The INT8
batch-numerics caveat applies only to its retained partial diagnostic. The
complete experiment's within-backend overlap checks remain mandatory.
