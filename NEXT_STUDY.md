# Smallest defensible next study (not yet executed)

Recommended scope: **Ambiguity-aware robustness for CPU text classifiers under diacritic loss**. Keep the Vietnamese classification problem and sparse implementation to control cost; do not begin a new LLM pretraining project or add many unrelated NLP benchmarks.

This is a research direction, not a claim of novelty or a submission-ready algorithm. If CAPC fails its frozen gate, do not tune it repeatedly against the exposed test sets. Treat those sets as exploratory from then on and acquire a new blind final evaluation.

## Mechanism to investigate

A surface form and its accentless form are not necessarily label-equivalent. Learn when normalization is a useful nuisance-removal operation and when it destroys task evidence. A stronger candidate should allow contradictory meanings to remain separable; CAPC only relaxes its paired penalty and still supervises fully folded views with the original labels, so it does not solve this problem.

One testable extension is a two-part predictor: a folded sparse expert plus a context-conditioned orthographic residual. A gate should depend on local ambiguity/context and be trained with *independently checked semantic-preserving pairs and semantic-changing contrast pairs*, rather than token class-frequency associations alone. Compare it against ordinary feature concatenation, scalar mixtures, a learned gate without ambiguity supervision and shuffled ambiguity labels. This is an unimplemented proposal and could overlap mixture-of-experts, multi-view learning and selective-invariance literature. It needs a separate novelty check before claiming originality.

## Minimum human work and independent evidence

1. Use a legitimate source of real noisy/canonical pairs such as ViLexNorm (CC BY-NC-SA 4.0; research use). Official train/validation/test boundaries must remain intact. This resource has normalization labels, not automatically trustworthy sentiment/emotion labels.
2. Obtain at least two Vietnamese annotators for a blinded audit of a prespecified stratified sample (for example 400 pairs, balanced over noise families, severity and task). Record label preservation, meaning preservation, ambiguity, disagreements and adjudication. The proposed number is a planning choice, not a statistical power guarantee. Estimate the required final sample size from a separate pilot effect and annotation variability.
3. Build a small independently checked contrast set where removing accents can erase a task-relevant distinction. Include both tasks and hard non-ambiguous controls. Split by original source/author where available and keep all variants together. Do not use the model's own predictions as ground truth.
4. Freeze a new untouched final set, preferably another domain or a second diacritic-rich language if transfer is a claimed contribution. Full cross-lingual experiments cost more and should be conditional on a convincing Vietnamese mechanism effect.

## Compute comparisons

Run PhoBERT and ViSoBERT as two matched reference models, plus fastText or another strong subword linear baseline; use the same final splits, seeds, text normalization and noise instances. Include ViSoLex/preprocessing where available and account for the normalizer's latency and memory. Existing paper numbers are context, not a fair direct comparison. A small GPU can shorten Transformer fine-tuning; no runtime or GPU-hour estimate is certified by this CPU-only pilot.

For sparse methods, measure real inference peak RSS, model-only and full-pipeline serialization, preprocessing time, batch=1 and batched throughput. Use representative document lengths and a warmed-up process; record CPU model, clock policy, threads and timing quantiles. This pilot's process-wide peak RSS is not enough for a deployment memory claim.

## Go/no-go milestones

- First: a reproducible gain over the strongest simple baseline and mechanism controls on validation, with a useful clean/noisy trade-off. Stop the variant if shuffled controls match it.
- Second: a positive effect on human-validated real noise and independently annotated ambiguity cases, not only synthetic in-family noise.
- Third: a frozen test with paired uncertainty estimates, error categories, efficiency trade-offs and reproducible artifacts. Report all failed settings and deviations.
- Finally: map the actual contribution to a journal's current aims/scope and ranking index/year. Q1 is a venue classification; there is no universal numerical novelty threshold or acceptance guarantee.

The fast milestone is a working, auditable prototype. The publication milestone depends on independent semantic validation and a mechanism that survives strong controls. They should not be conflated.
