# Novelty audit — before final confirmation
Checked 27 October 2026. This is a targeted prior-art screen, not proof of absence in all literature.

## Candidates considered

1. Stronger corruption regularization / adaptive normalization: generic invariance, noise marginalization and restoration-aware classification already exist. Repeating CAPC with a different weight or mixing rule would not supply a defensible Q1 method claim. Rejected as the main contribution.
2. Character n-gram retrieval / OCR-error channels: discriminative weighted finite-state language models and n-gram lattice/posterior methods are established; recent CharBM25 OCR retrieval further weakens a claim based on simply moving n-grams into retrieval. Not selected without a separate methodological gap.
3. Exact budgeted contextual sparse classification: selected for implementation because it supplies a testable algorithmic property and needs no fresh semantic annotation. Broad certified-robustness and dynamic-programming ideas are still prior art.

## Closest relevant primary sources

- Zhang, Albarghouthi & D'Antoni, EMNLP 2021, **Certified Robustness to Programmable Transformations in LSTMs**: https://aclanthology.org/2021.emnlp-main.82/ . ARC already certifies and trains recursive models over programmatic transformations. Dynamic programming over a transformation space is NOT new here. This is a central closest-method comparator, not background to dismiss.
- Abad Rocamora, Chrysos & Cevher, ICLR 2025, **Certified Robustness Under Bounded Levenshtein Distance**: https://arxiv.org/abs/2501.13676 ; official code https://github.com/LIONS-EPFL/LipsLev . LipsLev gives deterministic Lipschitz certificates for convolutional models under a broader edit-distance ball. BOLT's exactness on a restricted orthographic lattice must NOT be advertised as a stronger general Levenshtein guarantee. Published scores are not matched comparisons on the present datasets.
- Jia et al., EMNLP 2019, **Certified Robustness to Adversarial Word Substitutions**: https://aclanthology.org/D19-1423/ . Certified adversarial text training predates this project.
- **A Dynamic Programming Algorithm for Computing N-gram Posteriors**, EMNLP 2015: https://aclanthology.org/D15-1286/ . Lattices, n-grams and finite-state probability computations are established.
- **Discriminative n-gram language modeling**, Computer Speech & Language 2007: Publisher page: https://www.sciencedirect.com/science/article/abs/pii/S0885230806000271 . Global linear / log-linear models intersected with word lattices are established. No first weighted-automaton or first discriminative n-gram claim.

## Specific claims that can be tested

BOLT combines (i) raw and canonical token character features, (ii) adjacent-token contextual surface factors, (iii) exact weighted-cost separation preserving shared state decisions, (iv) class-balanced robust squared-hinge training by accumulated witness constraints, and (v) a fast certification procedure for this particular sparse architecture.

Provisional differentiation: exactness rather than interval relaxation for a constrained contextual sparse model; end-to-end alignment of training and the same corruption set; deterministic runtime instead of Monte Carlo certification. Each is narrow and must be tied to the defined architecture and threat model. These are engineering/method-specific hypotheses; established shortest-path, robust SVM and max-margin machinery does not become new because of an acronym.

Cannot claim: first certified text classifier; first dynamic-programming certifier; arbitrary edit-distance protection; semantic meaning preservation; robustness against arbitrary unknown errors; globally solved robust training merely because the oracle is exact; new benchmark as the main contribution; guaranteed Q1 acceptance.

Evidence required to call this a strong submission candidate: exactness against exhaustive enumeration, a useful accuracy/robustness frontier above invariant and random-augmentation controls, contextual benefit over unary robust models, attack-separation benefit above greedy training, meaningful certifier speed/coverage comparisons to the closest methods under matched perturbation sets, and external confirmation using existing labels. A simple-special-case implementation with modest gains is not automatically enough for Q1.

## Current novelty verdict

No identical complete implementation was located in the targeted searches. This is weak negative search evidence, not verification that the algorithm is globally new. Closest broad ideas are already present in ARC and older finite-state/robust optimization work. Therefore novelty is **plausible only at a narrow, architecture-specific method level and unconfirmed for Q1** before results and a full closest-method comparison. The final report must preserve this limitation even if benchmark scores improve.
