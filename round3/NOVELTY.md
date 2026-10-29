# Targeted prior-art audit — before confirmation

Checked 29 October 2026. This is a targeted screen, NOT proof that no identical method exists. No Q1 acceptance or global originality is guaranteed.

## Closest sources and overlap

- [CertDR, CIKM 2022](https://arxiv.org/abs/2209.06691), [official author PDF](https://jiafengguo.github.io/2022/CIKM2022-Certified%20Robustness%20to%20Word%20Substitution%20Ranking%20Attack%20for%20Neural%20Ranking%20Models.pdf): top-K certification for document substitutions with smoothed neural rankers already exists. Inspected the property/method and evaluation setup. Our finite COMMON QUERY perturbations and unchanged additive scorer are a different setting; published certification percentages are not matched baselines.
- [RobustMask](https://arxiv.org/abs/2512.23307), [full method](https://arxiv.org/html/2512.23307): randomized masking, pairwise ranking comparison, certified top-K defenses against document manipulation. Inspected Sections 3.1–3.2 and 4.1–4.2. Thus pairwise ranking certificates and protecting top-K are NOT new. It changes the smoothed neural model and uses a different threat model.
- [Relaxing Local Robustness, NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/file/8df6a65941e4c9da40a4fb899de65c55-Paper.pdf): relaxed/top-K safety properties and the distinction from strict set invariance are established. Inspected introduction/property discussion. Keeping a target inside top-K is not itself a new research problem.
- [Wong and Kolter, ICML 2018](https://proceedings.mlr.press/v80/wong18a.html): convex outer approximations, LP and dual certificates are established. An affine-envelope LP and its cutting-plane solution must not be sold as inventing convex verification or duality.
- [RetrievalGuard, ICML 2022](https://proceedings.mlr.press/v162/wu22o/wu22o.pdf), and [certified image retrieval, WACV 2023](https://openaccess.thecvf.com/content/WACV2023/html/Kakizaki_Certified_Defense_for_Content_Based_Image_Retrieval_WACV_2023_paper.html): broad retrieval stability/certification predates this project. Screened relevant descriptions; not claimed reproduced or fully reviewed.
- [Character-BM25 post-OCR retrieval, 2026](https://arxiv.org/abs/2609.21595): character-ngram retrieval for noisy strings already exists. Adding BM25 or moving ngrams into OCR/retrieval alone does not supply novelty.
- [Block-Max WAND, SIGIR 2011](https://research.engineering.nyu.edu/~suel/papers/bmw.pdf): safe score-bound pruning in retrieval is established. The primary PDF fetch timed out; the author/official documentation search establishes its relevance, but no claim of full-text inspection is made here.
- Pareto multiobjective dynamic programming, clique partitions, mixed-integer verification and LP integrality gaps are established combinatorial tools. The code does not claim their invention.

## Candidate-specific differentiation to test

The narrow hypothesis is a whole-corpus, finite-query-edit certificate for an unchanged additive ngram ranker that combines: (i) safe screening before materializing variant scores; (ii) a common-query count bound instead of independently counting possible pair reversals; (iii) DISCRETE simultaneous-promotion incompatibility, including cases not separated by a convex support bound; (iv) an anytime conservative graph cover with explicit resource-unknown outcomes; and (v) inspectable float bounds and actual query witnesses.

The graph/Pareto layer can be strictly stronger than the best convex relaxation because fractional mixtures of incompatible discrete edits can make several margins nonnegative. THEORY.md gives a diagnostic construction and the limitations of that argument. This is an implementation-specific contribution hypothesis, not a verified first theorem in general verification literature.

## Required falsification controls

Do not compare only to independent loose score intervals. Include exact pairwise+small-lattice enumeration, the best same-formulation generic LP, the custom support solver and generic MILP under recorded resources. A method that only improves a weak interval baseline, or only wins where trivial enumeration already solves the lattice, is not sufficient evidence for a new method claim.

Confirm useful gains on held-out queries, report conditional relevance and all datasets/budgets, and measure end-to-end cost rather than only a cheap postprocessing step. If generic MILP dominates in the relevant regime, disclose that and revise the research claim. Safe pruning is not a quality improvement of the underlying ranker.

## Current verdict

No identical complete specialization was identified in the targeted searches; this is weak negative evidence. The broader concepts have strong prior art. Confirmation has not yet run at this checkpoint. Q1-level novelty/readiness is UNCONFIRMED. A credible paper needs the empirical and theoretical advantage to survive matched controls plus a broader related-work review. This folder is not a submission-ready novelty certificate.
