# Pilot source amendment before observing channel-membership outcomes

The author-linked GitHub Typo Corpus v1.0.0 bucket returns404/NoSuchBucket.
The located community HF mirror has only text/correction columns and a
placeholder card, without verifiable original language/typo-label/source
mapping. Do not call that mirror the original labeled English corpus.
No membership results from it have been evaluated and no raw mirror data
are redistributed.

Use Roger Mitton's author/institution-hosted Wikipedia misspelling file:
https://www.dcs.bbk.ac.uk/~ROGER/wikipedia.dat
Documentation: https://www.dcs.bbk.ac.uk/~ROGER/corpora.html
The curator describes2455 misspellings of1922 words, derived from errors
made by Wikipedia editors and the Deorowicz/Ciura collection, with lexicon
filtering, British-form additions and documented corrections. This is a
curated type-level proxy, NOT naturally sampled search-query traffic or a
representative frequency distribution of all keyboard errors.

Pin raw bytes/hash and documentation hash before evaluating membership.
Keep the same100-pair smallest-SHA256(seed20261031|erroneous|corrected)
selection, max512codepoints per side, unique unequal raw pairs. Source is
already English spelling data: do not fabricate missing is_typo/language
labels. Interpret underscore as a space as the documented corpus format.
All eligible pairs participate before channel membership is inspected.
Normalization-only examples are separate, not counted as covered typos.
Use the unchanged frozen generator and exact changed-token budget.

Publish aggregate/source/pair-hash and line-number evidence only; raw corpus
bytes remain outside Git. The paper must name this actual source and its
curation/selection limits. This amendment supersedes only the unavailable
GTC source/filter part of PROTOCOL.md, not the statistical or membership
rules. It is not a new dataset contribution.
