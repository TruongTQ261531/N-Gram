# Reproducing the research

Start with the current English [reproducibility guide](docs/REPRODUCIBILITY.md). It covers all 16 recorded archive stages, component tests, pinned external inputs and separate fresh-run outputs.

```bash
python -m pip install -r requirements-all.txt
python verify_all.py
```

The older CAPC/BOLT/application instructions remain in the [historical Vietnamese guide](docs/LEGACY_REPRODUCE_VI.md). Frozen protocols and recorded outputs remain unchanged.
