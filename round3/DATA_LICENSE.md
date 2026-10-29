# Data, code and released evidence

The repository MIT license applies to this project's original code. It does not relicense upstream corpora, qrels, papers, Python dependencies or models.

The experiment downloads the public BEIR mirrors for SciFact, NFCorpus and FiQA, pinned by repository revision and byte SHA256 in `download_manifest.json`. The local source cards report CC-BY-SA-4.0; this is a report of mirror metadata, not an independent legal determination about all original content. Consult the original collection documentation and upstream terms before redistribution or use. Preserve attribution to the collection creators and BEIR maintainers.

- [BEIR / SciFact](https://huggingface.co/datasets/BeIR/scifact), [qrels](https://huggingface.co/datasets/BeIR/scifact-qrels)
- [BEIR / NFCorpus](https://huggingface.co/datasets/BeIR/nfcorpus), [qrels](https://huggingface.co/datasets/BeIR/nfcorpus-qrels)
- [BEIR / FiQA](https://huggingface.co/datasets/BeIR/fiqa), [qrels](https://huggingface.co/datasets/BeIR/fiqa-qrels)
- [BEIR project](https://github.com/beir-cellar/beir)

The public research evidence includes query/document identifiers, edit positions/characters, numerical outputs, existing relevance grades needed to verify metrics, source hashes, selected IDs, synthetic diagnostics and logs. Raw query/document text, the uploaded Word file, full indexes and cache pickles are not redistributed. Existing qrels are used for evaluation only; no new human annotations, LLM judgments, API-purchased labels or training labels were created in this round. Numeric relevance grades remain subject to their upstream provenance and terms.

Downloaded literature HTML/PDF files are local reading material and are excluded from publication. The related-work release contains bibliographic metadata, URLs, search records and our own summaries/access notes. A link or abstract screen does not imply endorsement or reproduction of the cited results.
