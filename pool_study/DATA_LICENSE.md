# Provenance and rights

The original corpora and queries belong to their upstream authors. This project does not claim authorship of ArguAna or SciDocs. Pinned Hugging Face BEIR cards identify both distributed datasets as CC BY-SA4.0; sources.json records exact revisions, URLs, source byte hashes and sizes. Preserve the upstream attribution and terms for original text and generated derivatives.

- ArguAna: [BEIR card](https://huggingface.co/datasets/BeIR/arguana), [Wachsmuth et al., Retrieval of the Best Counterargument without Prior Topic Knowledge, ACL2018](https://aclanthology.org/P18-1023/).
- SciDocs: [BEIR card](https://huggingface.co/datasets/BeIR/scidocs), [Cohan et al., SPECTER: Document-level Representation Learning using Citation-informed Transformers, ACL2020](https://aclanthology.org/2020.acl-main.207/).
- BEIR packaging/evaluation: [Thakur et al., BEIR, NeurIPS2021](https://arxiv.org/abs/2104.08663).

We release this folder's derived query, token-operation, factor-score and exact-oracle audit records with the inherited CC BY-SA4.0 attribution/ShareAlike notice. Changes: normalize NFC/lowercase/whitespace; retain first16 query tokens with truncation recorded; generate the explicitly declared compact edits; construct integer scorer weights; produce exhaustive computational top-k-set labels, certificate traces and measurements. These are synthetic edits of inherited real text, not natural typo logs. We downloaded no qrels, used no human relevance annotations, created no new human/LLM labels, and infer no semantic-preservation label from an edit.

Original corpus text is fetched from upstream by prepare.py and is not bundled into the source repository. Query text appears in derived records; ordered document IDs identify all matrix columns. Our new code files in pool_study and webapp/dist/pool.mjs/webapp/test-pool.mjs are available under the MIT license; see CODE_LICENSE. This does not relicense upstream corpora or the older codespell-derived synthetic audit data.

No visitor corpus/query data from the website is collected to construct this artifact. A user's uploaded text retains its own rights; exporting it through the application does not grant redistribution permission.
