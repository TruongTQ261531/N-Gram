# Cost and memory interpretation

The complete archived first pass contributes 2,910 whole-pipeline runs (970 per method). Its 3,774 total rows also include repeated subsets, retained separately. runtime_summary_970.csv uses repeat=0 only and reports p50/p95/p99/min/max with no completed-only filtering. Historic per-stage times and method-local peak RSS were not recorded; they remain explicitly missing.

The new 684 executions have fresh query construction/screening/materialization/pair intervals and separate kernel stages. Only the immutable warm index is shared. One numerical thread and deterministic hash order are used; one pass is exploratory, with no paired speed significance claims. CPU quota is four and memory limit 32GiB. Shared-host noise, allocator retention and a short small-domain validation process during the study are not controlled away.

Process RSS is sampled every 20ms plus stage endpoints, including the resident index and retained allocator pages. It is a sampled process footprint, not exact method-local peak or an estimate of private marginal allocation. OS cumulative HWM is a separate column and is never relabeled as per-method memory. Max sampled footprint is 3553.3 MiB.

The new common 20M dense-cell cap is additional to original solver caps. All 20 capped executions remain in denominators as full-corpus-rank unknowns. Eight are no-screen B=2 FiQA pipelines. Their lower incurred times cannot be used as a speed win because they skip materialization and lose output completeness. Source/model loading are excluded from warm-index pipeline costs.
