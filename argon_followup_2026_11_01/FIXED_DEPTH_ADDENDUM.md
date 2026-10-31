# Standard fixed-depth neural reranking controls

After the complete U/P,session and multiword outcomes, add standard BM25 top50
and top100 reranking controls before observing their new outcomes. Retain all
earlier results. Same128IDs,original integer lexical weights,same FP32ONNX
checkpoint,max256tokens,length bucketing,batch32,4CPUthreads and qrel policy.
Top50/100 include boundary ties; retain actual pool sizes. Run actual neural
inference on BOTH pools for all128raw queries, no result caching across pools.

For the SAME16hash cost-panel IDs, additionally rerun U and measure all three
conditions in fixed hash-rotated order, one execution each. Include tokenization,
padding,inference and ranking, excluding shared warm model/index and all pool
construction. Do not combine these fresh paired timings with old U/P timers.

Also check whether each CLEAN-query top50/100 pool would contain every edited
state's original lexical top10 from the full-domain replay. This is a diagnostic
of STATIC reuse only: ordinary per-query retrieval recomputes its candidates and
is not alleged to reuse a clean pool. U's static completeness target differs
from quality of one raw-query reranking. Report both scopes explicitly.
These controls test the alternative explanation of ordinary candidate expansion;
they are retrospective, not a new independent confirmation or a SOTA claim.
