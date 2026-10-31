# CPU runtime amendment before ONNX-dependent outcomes

The fixed cost panel contains119418 coarse-pool query/document pairs before
two repetitions. Initial PyTorch FP32 executions imply an impractical total
runtime for the90-minute cap. Stop that attempt without deleting or replacing
completed observations:21raw,1cost and20trace records, interrupted raw21 before
its session completed. Original code snapshot, file hashes and interruption
receipt remain in neural-torch-partial. This is an explicit resource amendment,
not a favorable query/model selection; no timed executions from the two
backends will be combined.

Use the SAME pinned checkpoint's author-distributed onnx/model.onnx (FP32),
source/hash in ONNX_SOURCE.json, ONNX Runtime1.23.2 CPU,4intra-op/1inter-op
threads, sequential execution, standard graph optimizations. Same16cost IDs,
all128queries, all20requests, float32 model, max-length256/fixed padding/batch32,
same cold result-cache policy and two cost repetitions. Record backend separately.
Repeat all planned ONNX measurements from the beginning; no outcome-based tuning.
Keep original90-minute cap for this complete attempt.

After ONNX measurements, obtain a PyTorch FP32 reference on every raw-U pair
(6175pairs over128queries), reusing the21already completed matching raw records
and measuring remaining raw-U records only. Report logit differences and top10
agreement, not an assumed exact transfer. The original cross-pool overlap checks
still apply within each backend. If exported ONNX differs, retain that finding.
The full-domain lexical replay is independent of the neural backend.
