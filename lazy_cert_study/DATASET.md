# Source, license and interpretation

WANDS is an existing Wayfair product-search relevance dataset, not a newly
collected corpus. Official source: https://github.com/wayfair/WANDS at commit
`3b74dcf4ba29ab8ff3e6a50b5b09fc627cb882b5`. The upstream README reports 480
queries, 42,994 products and 233,448 labeled query-product pairs; these input
counts are checked locally. The upstream license is MIT; preserve its notice
when redistributing any source data. `sources.json` pins exact source bytes.
The download/prepare commands store the source, license and large index
outside this checkout. No product descriptions are copied into this study.

Yan Chen, Shujian Liu, Zheng Liu, Weiyi Sun, Linas Baltrunas and Benjamin
Schroeder, *WANDS: Dataset for Product Search Relevance Assessment*, ECIR 2022.
This attribution is taken from the official source README, not a newly
verified publisher record.

The scorer indexes product_name + product_class + product_description from
all 42,994 products, without refitting on pools or truncating queries. Existing
Exact/Partial/Irrelevant labels are available for evaluation, never used to
choose queries or fit weights. Character BM25 with stored rounded integer
weights is a fixed subject of verification, not a claimed SOTA ranker.

Only the original search queries come from WANDS. Edits and request sequences
are deterministic synthetic constructions. They are NOT observed user
sessions or naturally paired spelling mistakes. The derived exact unions
are computational audit labels, not new human relevance annotations or
proof that an edit preserves meaning. Reusing WANDS plus adding an oracle
does not by itself establish dataset novelty.
