# Literature and novelty audit (checked 27 October 2026, Asia/Bangkok)

Search scope: targeted primary-source web searches for Vietnamese noisy text classification, diacritics, lexical normalization, selective invariance, marginalized corruption, and multilingual typo robustness. This is a focused novelty screen, not an exhaustive systematic review. Abstract/full-page metadata inspected; no claim that every full paper or implementation was reproduced. Publications dated only October 2026 require final release/version checks before submission.

| Work | Evidence inspected / date | What it already establishes | Implication for this project |
|---|---|---|---|
| How Well Do Decision Models Transfer to Vietnamese? An Empirical Study of Text Classification | arXiv abstract, submitted 22 Oct 2026; https://arxiv.org/abs/2610.31422 | 4 decision models, 13 classification settings, teencode/typo/diacritic robustness; removing diacritics is particularly damaging | A new table of models under the same noises is insufficient novelty; its zero-shot models are not the same setting as supervised n-grams |
| ViSoLex | COLING 2025 demo, https://aclanthology.org/2025.coling-demos.18/ | Vietnamese NSW lookup and model-based normalization using weak supervision | Normalization and a teencode dictionary are existing methods; must compare normalization or state it is missing |
| ViLexNorm | EACL 2024, https://aclanthology.org/2024.eacl-long.85/ ; official corpus https://github.com/ngxtnhi/ViLexNorm | Real social-media normalization pairs | Potential train-only noise estimation / human-checked real-noise evaluation resource, not a ready-made sentiment-labeled test |
| ViGoEmotions | EACL 2026, https://aclanthology.org/2026.eacl-long.129/ | 20,664 comments, fine-grained emotions, preprocessing/emoji/ViSoLex comparisons | Plain downstream preprocessing evaluation is established; emoji preservation matters |
| FLUKE | Findings EACL 2026, https://aclanthology.org/2026.findings-eacl.269/ | Task-dependent linguistic perturbations with human validation | Synthetic character noise alone is a narrow evaluation; fluent and semantic perturbations matter |
| MulTypo | ACL 2026, https://aclanthology.org/2026.acl-long.729/ | Multilingual language-specific keyboard errors and robustness | Our simple keyboard-neighbor operator is a stress test, not a calibrated human typing simulator; do not claim realistic error distributions |
| The Degree of Language Diacriticity and Its Effect on Tasks | CAWL 2026, https://aclanthology.org/2026.cawl-1.1/ | Information-theoretic frequency/ambiguity metrics across 15 languages | Diacritic ambiguity itself is not a new discovery |
| Uncertainty-driven Partial Diacritization for Arabic Text | UncertaiNLP 2025, https://aclanthology.org/2025.uncertainlp-main.1/ | Selective retention of diacritics through uncertainty | Selective handling of diacritics is prior art, although the task/direction differs |
| One Meaning, Many Romanizations | MRL Oct 2026, https://aclanthology.org/2026.mrl-1.29/ | Selective stability: equivalent spellings should contract while meanings remain separated; lightweight representation repair | Very close conceptual prior art. CAPC cannot claim the general selective-stability idea as new |
| Learning with Marginalized Corrupted Features | ICML 2013, https://proceedings.mlr.press/v28/vandermaaten13.html | Robust predictors from corruption-aware expected losses | Corruption-aware linear optimization is long established |
| Counterfactual Invariance to Spurious Correlations in Text Classification | NeurIPS 2021, https://papers.nips.cc/paper_files/paper/2021/hash/8710ef761bbb29a6f9d12e4ef8e4379c-Abstract.html | Different causal settings need different invariance regularizers | Do not label generic consistency a novel causal method |
| Trustworthy AI Suffers from Invariance Conflicts and Causality is The Solution | ICML 2026 position paper, https://proceedings.mlr.press/v306/binkyte26a.html | Conflicting invariance requirements / selective invariance | Conceptual motivation exists; this project supplies no causal identification |

## Candidate and what is actually specific

CAPC uses character n-grams and a convex supervised squared-loss objective, plus a paired clean-to-folded score-consistency penalty weighted by train-only, out-of-fold surface/folded-family label disagreement. The specific heuristic weighting and efficient sparse implementation are the experimental candidate. Components (TF-IDF, ridge, data augmentation, paired consistency, JSD, cross-fitting) are established. Renaming their combination does not establish algorithmic novelty.

Objective (all supervised views weighted to sum to one per original row):

L(W) = sum_i (s_i/3) sum_{v in {raw, folded, sampled-noisy}} ||phi(v_i)W - onehot(y_i)||²
       + alpha ||W||_F²
       + lambda sum_i s_i r_i ||[phi(raw_i)-phi(folded_i)] W||².

s_i is inverse-frequency class balance. r_i=exp(-4 max_t JSD(P(Y|surface=t),P(Y|folded=fold(t)))), estimated on other training folds. Here ambiguity is a noisy token-label association proxy, NOT proof of semantic ambiguity. Rare spellings, class correlations, label imbalance and maximum aggregation can all make the weights unreliable. The penalty only compares raw and fully folded views, so it does not guarantee robustness to other noise families. Every variant also receives fully folded supervised training: weighting the penalty does NOT remove the label-preservation assumption for those examples.

For alpha>0 this is a strictly convex quadratic with a unique minimizer. Append sqrt(lambda*s_i*r_i) times the difference-feature row with a zero target, and solve sparse ridge regression. No dense 30,000 x 30,000 inverse is formed. Strict convexity and solvability are standard facts, not new contributions. This implementation uses LSQR and finite tolerances; the full-data global optimum is not independently certified, only a toy stationarity check is performed.

A useful deployment variant might avoid destructive normalization under *context-specific semantic ambiguity* and use risk-controlled abstention. That would require independently validated ambiguity pairs, calibration under deployment conditions, and evidence beyond this pilot. It is an untested research direction, not an achieved contribution.

## Submission decision

Two existing datasets with synthetic perturbations can falsify a poor lightweight idea quickly, but cannot establish Q1 readiness. Candidate must outperform augmentation/uniform/shuffled controls on both tasks with confidence intervals, retain clean performance, show reliable effect on real human-validated noise and ambiguity pairs, and compare against matched neural/normalizer baselines. Extra noise types or extra models alone do not repair a missing mechanism contribution.

Potential journal *scope targets*, not acceptance promises: Expert Systems with Applications for a substantive applied system; Information Processing & Management for a broader information-processing/retrieval framing. Do not change scope just to match a journal title. Their publisher aims/scope pages returned 403 during this audit. A university research institute lists Q1 for 2025 metrics at https://www.iit.comillas.edu/publicacion/info_revista/en/60/expert-systems-with-applications and https://www.iit.comillas.edu/publicacion/info_revista/en/659/information-processing-management . This is secondary ranking evidence, not an independently verified JCR/Scimago record. Confirm the exact index, year and subject category required by the user's institution before submission. No journal-ranking claim is used to assess the algorithm's quality.

## Algebraic novelty check

For paired squared-loss predictions a,b and target y:

||a-y||² + ||b-y||² + lambda||a-b||²
= 2||((a+b)/2)-y||² + (1/2+lambda)||a-b||².

Thus pairwise consistency merely changes the disagreement weight in a familiar quadratic decomposition. This identity further limits any novelty claim about the objective itself. An independent numerical identity check was added to `test_integrity.py`; it does not change the experimental models or frozen configurations. A meaningful contribution would have to come from the ambiguity estimator or another verifiable mechanism, not from calling the quadratic penalty new.
