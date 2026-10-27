# Disclosed run correction

A first complete validation selection and partial test execution used a faulty keyboard operator: most letter substitutions were identity mappings. The bug was discovered by code inspection, before test F1/accuracy values were inspected. The partial run was terminated. The source, protocol, selected parameters, hashes and logs were retained locally in `superseded_keyboard_v0/` (excluded from publication to avoid mixing invalid and valid results). The specific defect is documented in PROTOCOL.md. Test arrays from that run, if present, are not used in the final report.

Correction: explicit 26-letter non-identity adjacent-key table, plus an exhaustive single-letter test. Both validation selection and all test runs are rerun. Final hashes refer to v1. The first data loading attempt also caught an empty VSFC validation row through an integrity assertion; dropping the entirely missing row restores the expected count of 1,583.

These corrections do not constitute test-set model tuning. Timing and fit counts in the final report refer to the final completed protocol, not discarded computational attempts. This is a local timestamp/hash audit, not external preregistration.
