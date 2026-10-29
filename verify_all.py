"""Verify both recorded studies without downloading data or fitting models."""
from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

def main():
    count = 0
    for line in (ROOT / "integration_checksums.sha256").read_text(encoding="utf-8").splitlines():
        expected, name = line.split("  ", 1)
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Integration checksum mismatch: {name}")
        count += 1
    print(f"Integration checksums verified: {count} files", flush=True)
    for label, script in [
        ("CAPC recorded archive", "verify_results.py"),
        ("BOLT recorded archive", "round2/verify_recorded.py"),
    ]:
        print(f"Checking {label}", flush=True)
        subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)
    print("Both recorded studies verified. Hybrid evaluation and Q1 novelty are not established.", flush=True)

if __name__ == "__main__":
    main()
