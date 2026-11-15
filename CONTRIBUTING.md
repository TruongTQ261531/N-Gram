# Contributing

Please open an issue or pull request describing the scientific or maintenance change and how it was checked. Keep claims tied to a named scorer, edit channel, cohort and comparison.

- Preserve frozen source, protocols, query selections, proofs and recorded results. Put new experiments in a separate directory and disclose whether they are prospective or retrospective.
- Keep capped and unknown outcomes in the selected-query denominators. Report negative findings and opposing baseline results alongside improvements.
- Run `python verify_all.py` before submitting changes to archive integration. Run the relevant component tests listed in [Reproducibility](docs/REPRODUCIBILITY.md) for code changes.
- If a documentation-only change affects release checksums, update only its packaging entries and enclosing manifests, and explain why. Do not change experimental freezes to make checks pass.
- Keep manuscript TeX/Bib/PDF files, raw corpora, index caches, credentials, personal input corpora and restricted upstream software outside Git. Existing scientific plot PDFs are retained as evidence.
- Respect upstream licenses. The project MIT license does not override dataset, dictionary or third-party software terms.

Historical dated paths remain stable because source receipts refer to them. Prefer a clear landing page and links over moving frozen experimental modules.
