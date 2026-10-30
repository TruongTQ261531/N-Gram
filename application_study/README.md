# Browser-local application and exact audit data

Read [REPORT_VI.md](REPORT_VI.md) for the measured contribution and its limits. [PROTOCOL.md](PROTOCOL.md) and `freeze.json` were published before audit outcomes at commit8055553. Existing CAPC/BOLT/round3 evidence is unchanged. This is an application/data contribution candidate, not verified Q1 novelty.

The browser application imports a local corpus, retrieves documents, certifies a sufficient retention depth under a finite error model, exposes counterfactual witnesses and exports self-contained proof/dataset bundles. Its integerized BM25 scorer is explicitly different from round3's float scorer. The live browser limit is500docs/500kcharacters/16tokens; it is not full FiQA online serving.

The v0.1 synthetic/semi-synthetic audit set contains48docs,48seeds,12source families and288 cases. All334,815states are independently checked using arbitrary-precision Python integers. Curated spelling errors derive from a pinned, attributed CC BY-SA3.0 codespell dictionary. No human/LLM semantic relevance labels are created. It is not natural query traffic. Cover improves17cases by one depth position but does not improve acceptance at the prespecified caps; see the report before interpreting gains.

## Verify original evidence

```bash
node webapp/test-engine.mjs
python application_study/check_archive.py
```

Node24 and Python3.12 were used. The oracle verifier uses only Python's standard library. It recomputes every token/document score from integer weights, enumerates every allowed choice, checks all stored ranks/witnesses/conflict edges/groups and source-family isolation. SHA256 detects changed bytes; neither hashing nor tests establish global novelty.

## Recompute in a separate checkout

Back up `application_study/results/` first. The generator refuses to overwrite its original audit file. Keep the source/input freeze unchanged; these already-viewed inputs are not a new prospective validation.

```bash
# Only if recreating the optional dictionary from the pinned upstream source:
python application_study/import_dictionary.py --data-dir webapp/dist/data
# Move original generated results outside this working folder before the next command.
node application_study/build_dataset.mjs
python application_study/verify_oracle.py
python application_study/analyze.py
```

Wall times/compressed bytes can differ on another platform; preserve discrepancies. Read DATA_LICENSE.md before redistributing dictionary-derived records or user corpora.

## Source and deployment

`webapp/dist/` is a buildless static application. Serve it locally with `python -m http.server 4173 --directory webapp/dist`; open localhost4173 in your browser. The ESM Web Worker requires HTTP(S), not file://. User corpus/query processing is local. There is no automatic collection/publishing of visitor inputs. The download can contain the visitor's corpus, so review before sharing it.

The Sites identity is in `webapp/.openai/hosting.json`; reuse that identity for updates, never register a duplicate. `deployment.json` records the actual deployed URL/version/source after successful publication. No deployment credentials are committed. Related-work screening and its access limits are in RELATED_WORK.md and sources.json.
