# Discrete shared-query retention certification for n-gram retrieval

Research round 3, 29 October 2026. This folder studies a NEW CANDIDATE IMPLEMENTATION, not a verified globally new or Q1-ready algorithm. The prior CAPC and BOLT studies remain unchanged. No CAPC–BOLT hybrid was assumed effective.

At this checkpoint the development stage is complete and confirmation is about to run. Do not interpret development scores as confirmation. The active plan is [PROTOCOL_RETENTION.md](PROTOCOL_RETENTION.md); [PROTOCOL.md](PROTOCOL.md) preserves the failed strict-set-invariance pilot. The code/configuration freeze is in results/confirmation_freeze.json. A GitHub commit must exist before confirmation execution.

The fixed character-BM25 scorer is unchanged by certification. The candidate bounds the worst-tie rank of its clean winner under a finite token-edit model. It uses safe whole-corpus screening, exact pairwise margins, a shared-query affine LP, and discrete pair-incompatibility covers. Small query lattices are exhaustively enumerated; generic LP and MILP are matched controls. Standard methods used here are not claimed as newly invented. See [THEORY.md](THEORY.md) and [NOVELTY.md](NOVELTY.md).

## Reproduce on CPU

Python 3.12. No GPU, torch, paid API or fresh human annotation is required.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r round3/requirements.txt
python -m unittest discover -s round3 -p 'test_*.py'
python round3/verify_freeze.py
python round3/download.py
python round3/run.py prepare --dataset scifact
python round3/run.py prepare --dataset nfcorpus
python round3/run.py prepare --dataset fiqa
python -u round3/experiment.py --dataset scifact --phase confirmation --limit 100 --label confirmation
python -u round3/experiment.py --dataset nfcorpus --phase confirmation --limit 100 --label confirmation
python -u round3/experiment.py --dataset fiqa --phase confirmation --limit 100 --label confirmation
```

Use a clean checkout for a fresh replication. Keep the committed evidence outside the working results directory before regenerating it. Preserve the freeze/IDs needed by the driver. Do not describe a rerun after seeing results as a new independent confirmation. Cache pickle files are local self-generated files, not downloaded or published model artifacts.

The raw corpus is indexed in full (5183/3633/57638 documents). Queries are bounded to 32 normalized whitespace tokens and 100 selected test IDs per corpus. This is not full-query/full-test BEIR SOTA. The guarantee covers only one specified operation per changed original token and at most three changed tokens, not arbitrary edit distance or semantics. Relevance uses existing original-query qrels; ranking stability is a different property.

The managed development environment has a 2-core quota and 8 GiB RAM. Local execution can provide an independent replication or more compute; it does not by itself create novelty or increase the assistant's reasoning ability. Whole-corpus index caches can require several GiB of RAM at runtime. Do not run all datasets concurrently on an 8 GiB machine.

Source revisions/hashes are in download_manifest.json. Mirror cards report CC-BY-SA-4.0; consult original source terms too. Raw corpora, source cards and complete indexes are not redistributed in this repository.
