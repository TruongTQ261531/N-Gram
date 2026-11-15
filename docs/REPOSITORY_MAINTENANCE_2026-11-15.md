# Repository maintenance — 15 November 2026

Scientific baseline: `33c0d031740342ef4ac4e761c70d92ac819111f1`. The branch includes the previously local November 5 follow-up and self-review commits, so the landing page describes records actually included in the checkout.

## Changes

- Replace the root README with an English overview of current tasks, results, limitations and reproduction commands.
- Add an English results/provenance guide, reproduction guide and contribution policy; retain the older Vietnamese reproduction instructions as a historical guide.
- Update machine-readable project status; stop advertising an owner-private deployment as a public service.
- Extend the integrated verifier to all 16 archived stages and add both November 5 audits to CI.
- Prevent the historical round3 report helper from regenerating an obsolete manuscript or overwriting the maintained stage README.
- Add manuscript/build/cache exclusions for future untracked files. Existing proof receipts, factors, plots and measured logs remain versioned.

## Removed from the current checkout

| File | Reason |
| --- | --- |
| `round3/MANUSCRIPT.md` | Obsolete generated draft; manuscripts are maintained separately from GitHub |
| `round3/bibliography.bib` | Bibliography for that obsolete draft; paper sources remain outside the repository |
| `application_study/build.log` | Redundant browser build transcript; static application needs no build step |
| `application_study/engine-tests-direct.log` | Duplicate test execution transcript; canonical `engine-tests.log` and test source retained |
| `application_study/engine-tests-release.log` | Duplicate test execution transcript; canonical test evidence retained |

No Git history is rewritten. Historical commits still contain these files. No numerical result, factor matrix, prediction array, proof witness, dataset attribution, experimental algorithm, protocol or experimental freeze is deleted or altered. In particular, the split gzip parts in the full-domain UTK archive and scientific plot PDFs in round3 remain required archive material.

## Release-manifest maintenance

The affected packaging manifests are `results/checksums.sha256`, `round3/checksums.sha256`, `application_study/checksums.sha256`, `exact_pool_study/checksums.sha256` and their parent `integration_checksums.sha256`. Existing entries are refreshed only for deliberately edited presentation/helper files; the five removed files are dropped from their release inventories. New current documentation and verifier/workflow entry points are covered by the integration manifest. The exact-pool release manifest changes only because the historical project-review document's link to the removed draft is corrected.

Experimental selection/result locks, source freezes, follow-up `MANIFEST.json` files and all scientific payloads retain their original bytes. Packaging integrity is checked again after cleanup; refreshing documentation hashes is not a new experiment or a replacement for scientific validation.

## Validation

- All 16 recorded archive stages pass the expanded integrated verifier, without raw-data downloads or new optimization benchmark runs.
- 90 Python unit tests pass across the retained retrieval, pool and audit components. Unrelated legacy modules are tested in separate processes to avoid their shared top-level import names.
- Node.js 24 engine tests pass all four test groups (including 64 independent exhaustive checks); the pool test passes 600 randomized corpus/budget/K cases.
- The report helper is smoke-tested with a temporary output directory: all historical numerical table rows are unchanged, the maintained README is untouched and no manuscript is regenerated.
- Current landing/reproduction/result documentation has no missing local links. Git whitespace checks pass. Existing experimental code, locks and numerical outputs are unchanged relative to the scientific baseline.

These checks cover the named archives and components. They are not a claim that every possible objection, upstream download or historical data-dependent test has been exhausted.
