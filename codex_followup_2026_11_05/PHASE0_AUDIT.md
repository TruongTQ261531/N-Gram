# Phase 0 audit

PASS on an isolated detached worktree of `63ceeda350a0f7e3c9138c3b1232d2ea06e49054`. The original checkout and frozen results were not used as scratch outputs. `python verify_all.py` passed. `python -m unittest discover -s round3 -p 'test_*.py' -v` passed all 18 tests, including 1,200 exhaustive comparisons and 210 high precision interval checks. Six additional matched-ablation tests passed before the panel freeze.

The 970 rows join by dataset and original query ID without duplicates or omissions. Primary LP=227 and Discrete=259; later full-cohort MILP=260; decision audit=266 robust/704 nonrobust. Later analyses are explicitly retrospective. No prospective registration is implied.

The uploaded follow-up brief is reference material. The user's direct instruction authorizes additional bounded experiments and manuscript editing, superseding the brief's default instruction to postpone manuscript edits. No publication or remote Git mutation is part of this follow-up.
