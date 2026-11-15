# Certified lexical retrieval under shared query edits

[![Research archive](https://github.com/TruongTQ261531/N-Gram/actions/workflows/integration.yml/badge.svg)](https://github.com/TruongTQ261531/N-Gram/actions/workflows/integration.yml)
[![Reviewer audits](https://github.com/TruongTQ261531/N-Gram/actions/workflows/reviewer-audit.yml/badge.svg)](https://github.com/TruongTQ261531/N-Gram/actions/workflows/reviewer-audit.yml)
[![License: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)

Research software and recorded experiments for **certifying a fixed character-n-gram lexical retriever under a finite set of shared query edits**. The central question is whether the clean-query winner remains in top-K for every allowed edited query, using the same edit choices against all competing documents.

The repository also studies exact possible-result unions for offline auditing. These are complementary tasks with different scoring and edit contracts, rather than a single evaluated online or neural retrieval pipeline. Earlier CAPC/BOLT classification studies remain available as historical research.

Working manuscript title: *Bounding the Worst-Case: Certified Lexical Retrieval under Shared Query Edits*. Manuscripts, submission files and bibliography files are maintained separately from this code repository. This repository does not imply publication or acceptance.

## Current evidence

The original independent replication contains **970 queries**, at edit budget B=2 and K=10. Later exact-decision auditing identifies 266 robust and 704 nonrobust cases.

| Dataset | Queries | Audited robust | Best LP + enumeration | Discrete (original) | MILP + enumeration (later numerical control) |
| --- | ---: | ---: | ---: | ---: | ---: |
| SciFact | 199 | 123 | 115 | 123 | 123 |
| NFCorpus | 223 | 47 | 41 | 45 | 47 |
| FiQA | 548 | 96 | 71 | 91 | 90 |
| **Total** | **970** | **266** | **227** | **259** | **260** |

The original Discrete-versus-LP comparison passes the prespecified Holm-adjusted tests on two of three datasets. Discrete does **not** uniformly dominate MILP. Later optional refinement certifies all 266 audited robust cases with zero certifications among the 704 audited nonrobust cases, but is a **retrospective all-query replay**, with additional cost, rather than a new independent confirmation.

Further validation includes:

- **970-query graph ablation:** full support/Pareto gives 259 certificates versus 250 for equal-weight support, with the same frozen prefix. This isolates the graph component; it is not 970 fresh solver or timing runs.
- **36-query sensitivity panel:** 684 fresh pipeline executions and 2,736 threshold decisions, including every capped/unknown outcome. It does not establish uniform component dominance.
- **Independent tiny-domain oracle:** 396 exact-dyadic checks, 185 nonvacuous positive outcomes and zero unsound bounds in the tested cases. This is validation evidence, not a formal proof of the complete software stack.

The complementary **WANDS offline union audit** uses 128 queries, 42,994 products and 6,684 finite query states. All 128 unions match full enumeration. Median coarse-pool and exact-union sizes are 2,613 and 45. The original matched construction comparison gives a paired geometric speed ratio of **2.3474×** (95% bootstrap interval 2.0824–2.6293), winning 107/128 queries against the faster executed per-query offline control. The **20-request session gate fails**: 38/128 wins and ratio 0.7472. No interactive speedup or observed session break-even is claimed.

See [Results and scope](docs/RESULTS_AND_SCOPE.md) for provenance, timing definitions, negative findings and the distinction between original and retrospective evidence.

## Quick start: verify the recorded evidence

Use Python **3.12** on Linux. This checks the archived records without downloading raw corpora or rerunning optimization benchmarks.

```bash
git clone https://github.com/TruongTQ261531/N-Gram.git
cd N-Gram
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-all.txt
python verify_all.py
```

The complete verifier checks release hashes and all 16 archive stages, including the two November 5 follow-ups. It fails if a required archive is missing or inconsistent. Scientific libraries are pinned; gzip/NPZ factors, proof receipts, solver logs and split archive parts are intentional reproduction inputs. A full checkout is several hundred MB.

For a focused check of the latest audits:

```bash
python -m codex_followup_2026_11_05.verify
python -m self_review_2026_11_05.verify
python -m unittest codex_followup_2026_11_05.test_experiments -v
python -m unittest self_review_2026_11_05.test_graph_review -v
```

For unit checks, local browser tests, pinned external inputs and fresh experiment runs, see [Reproducibility](docs/REPRODUCIBILITY.md). Re-execution requires a separate working copy and must preserve the original evidence.

## Repository guide

| Location | Purpose |
| --- | --- |
| [round3/](round3/) | Central float64 retention certifier, theory, original 300-query confirmation and independent 970-query replication |
| [reviewer_audit_2026_10_31/](reviewer_audit_2026_10_31/) | Backend bridge, full-cohort MILP and controlled runtime audits |
| [decision_audit_2026_10_31/](decision_audit_2026_10_31/) | Exact robust/nonrobust decisions and observed correction-channel membership |
| [claims_consolidation_2026_11_01/](claims_consolidation_2026_11_01/) | Closest-work mapping and retrospective all-query refinement |
| [codex_followup_2026_11_05/](codex_followup_2026_11_05/) | Complete cohort join, fresh sensitivity panel and independent tiny-domain oracle |
| [self_review_2026_11_05/](self_review_2026_11_05/) | Full-cohort graph ablation, fixed-grid linear-support diagnostic and qrel strata |
| [lazy_cert_study/](lazy_cert_study/), [exact_pool_study/](exact_pool_study/), [pool_study/](pool_study/) | Index-first screening, offline unions and session controls |
| [utk_full_domain_2026_11_01/](utk_full_domain_2026_11_01/), [utk_adapter_study/](utk_adapter_study/) | Finite-domain RSA/JAA adaptations and native-output fixtures, with performance limits documented |
| [argon_followup_2026_11_01/](argon_followup_2026_11_01/) | Graph refinements, natural-correction and neural-cascade boundary analyses |
| [webapp/](webapp/), [application_study/](application_study/) | Local browser demonstrator and independent integer-score oracle |
| Root study files and [round2/](round2/) | Historical CAPC/BOLT classification experiments; separate tasks and metrics |

Dated directories and legacy reports retain their original paths for source freezes and provenance. The root README, [results guide](docs/RESULTS_AND_SCOPE.md), [reproduction guide](docs/REPRODUCIBILITY.md) and [PROJECT_STATUS.json](PROJECT_STATUS.json) describe the current project; dated planning documents describe their historical stage.

## Guarantees and boundaries

- **Retention:** fixed float64 character-BM25 scorer, NFC/casefold normalization, at most 32 query tokens and the declared finite per-token delete/swap/repeat/QWERTY edit channel. Bounds use the documented outward numerical enclosures and conservative ties; the implementation is not a mechanized verification of SciPy/BLAS/HiGHS.
- **Offline union:** integerized weights (scale 10^6), NFC/lowercase normalization and a separate compact full-query edit channel. A measured backend bridge does not make the two contracts universally equivalent.
- **Scope:** certificates concern lexical ranks under allowed edits. They do not certify relevance, preservation of meaning, unrestricted spelling errors, neural top-K, RAG answers or global SOTA. Synthetic audit cases are not a newly collected natural-query dataset.

## Local browser demonstrator

The static application runs locally; no build step is required:

```bash
python -m http.server 4173 --directory webapp/dist
```

Open <http://localhost:4173>. The browser limits (500 documents, 500,000 characters and 16 tokens) differ from the Python corpus experiments. This is a demonstrator, not a public production service. See [application documentation](application_study/README.md).

## License, data and contributions

Project code is under the [MIT license](LICENSE). Third-party corpora, dictionary-derived material and upstream software retain their own terms; see [round3 data terms](round3/DATA_LICENSE.md), [pool data terms](pool_study/DATA_LICENSE.md), [application data terms](application_study/DATA_LICENSE.md) and [UTK acquisition notes](utk_adapter_study/). Raw corpora, indexes and restricted upstream dependencies are not redistributed here.

Please follow [CONTRIBUTING.md](CONTRIBUTING.md): preserve frozen evidence, keep new runs separate and report limitations alongside gains. The [maintenance record](docs/REPOSITORY_MAINTENANCE_2026-11-15.md) explains the conservative repository cleanup.
