# Recovered original GTC archive: additional preselected multiword pilot

After the JFLEG outcomes, an extended source search located a 2020-09-06
Internet Archive capture of the EXACT author-documented S3 download URL.
Original S3 still returns404/NoSuchBucket. The43,769,081-byte replay payload's
base32 SHA-1 matches the CDX digest IDRMZ4JVCEGPABJ6FFSXE42INRS2LBPW exactly;
SHA256/source/timestamp are pinned in GTC_SOURCE.json. This is archived original
content, not the unlabeled HF mirror. Its schema retains repo/commit and the
original language,prob_typo,is_typo fields. This is provenance evidence, not
author-signed cryptographic authentication or human verification of each edit.

Add a separate200-pair pilot before observing its membership metrics. Retain
ALL earlier panels/outcomes; do not replace them or call this independent
preregistered confirmation. English src.lang=tgt.lang=eng and is_typo is TRUE
are automatically inferred corpus labels, not human semantic gold. Require
>=2normalized tokens on EACH side, unequal normalized text, <=2048codepoints
each side. No edit-distance,changed-position,32-token-scope or membership filter.
Deduplicate raw(src,tgt)text pairs; keep first source occurrence. Choose200
smallest SHA256(argon-gtc-v1|src\0tgt), preserving source line/edit index/repo/
commit/pairhash. Write selection BEFORE calling unchanged membership(B2).
Use tgt as clean and src as erroneous; record B1/B2,categories/operations and
>32-clean-token failures. Keep code/context errors and out-of-channel cases.

No raw corpus,raw text or derived text is published; each upstream repository's
rights remain applicable as documented by the original authors. Publication
attribution uses the already cited GitHub Typo Corpus paper. This source is
natural code-repository correction data, not natural search-query logs or new
relevance annotation. The archive recovery does not imply the old source
availability statements were false at the time; document the new recovery.
