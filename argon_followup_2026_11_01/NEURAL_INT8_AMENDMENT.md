# Dynamic-INT8 CPU scorer amendment, before dependent outcomes

The ONNX FP32 attempt showed no material throughput benefit over PyTorch FP32.
Retain its5raw/5trace records (no completed cost block) and interruption receipt.
Neither partial FP32 attempt supplies a full128-query speed claim.

Run the complete fixed protocol using the SAME model repository/revision's
author-provided onnx/model_qint8_avx512_vnni.onnx, pinned in
ONNX_INT8_SOURCE.json. This is a DISTINCT NUMERICAL SCORER: dynamic INT8
quantization, FP32 logits. Do not claim exact equivalence to the PyTorch model.
The128IDs,16costIDs,256-token fixed padding,batch32,4CPU threads,2repeats,
20requests,cache rules and90-minute cap remain fixed. Both U and P use this
same scorer, so paired timing comparisons are within this backend only.

Afterward obtain the predeclared6175-pair raw-U PyTorch FP32 reference on
ALL128IDs, reusing21completed raw records from the first attempt. Record
max/mean logit discrepancies, exact ordered-top10 and top10-set agreements.
Do not tune quantization, select a favorable model or merge cross-backend timings.
If results differ, explicitly limit downstream results to this CPU INT8 scorer.
Lexical containment and full-domain cascade input identity do not require
neural-backend equivalence and remain separate from neural robustness claims.
