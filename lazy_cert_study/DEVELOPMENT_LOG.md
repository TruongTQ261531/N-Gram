# Development corrections before confirmation

- The first four-query smoke test used a helper that unnecessarily rebuilt a
  full-corpus sparse transpose for the parent control. This made its timing
  baseline artificially expensive. Inspection caught the issue before any
  confirmation run or performance claim. Both materialization and serving
  now reuse the shared full transpose when all documents are selected. The
  first smoke output is retained outside Git as development-smoke.jsonl.gz
  and is superseded for timing comparisons; a complete rerun is required.
- The screen initially rescanned all index weights to get an integer range
  guard on every query. The maximum is query-independent, so it is cached
  with the shared warm index. This is standard preprocessing, not novelty;
  its cost must be reported separately from per-query measurements.
- Independent oracle recursion prunes over-budget prefixes. Cartesian
  enumeration followed by filtering would waste exponential work even on
  low-budget long queries. Neither version is a new search algorithm.
- Development v3 added a batched exhaustive comparator. On early development
  queries, extracting all vocabulary weights of a projected document pool was
  more expensive than querying the relevant postings. v4 extracts only the
  feature rows reachable by the declared query lattice. This standard sparse
  optimization is shared by parent, batched and screened projected serving;
  it is not credited as a new verification mechanism. v3 source and outputs
  are preserved outside Git; confirmation has not started.
- Input integrity checks stopped quality.py before metrics because WANDS
  contains repeated query-product judgments (1,467 pairs;14 discordant).
  Protocol now fixes maximum-grade aggregation before any relevance metric
  or confirmation run. Raw labels are never rewritten. A source dataset
  containing duplicates is not silently treated as a unique qrels table.
