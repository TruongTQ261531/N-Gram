"""Verify every recorded research stage offline, without rewriting evidence."""
from pathlib import Path
import hashlib
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


STAGES = [
    ("CAPC", ("verify_results.py",)),
    ("BOLT", ("round2/verify_recorded.py",)),
    ("Original retention and replication", ("round3/verify_archive.py",)),
    ("Browser integer-score audit", ("application_study/check_archive.py",)),
    ("Reusable pools", ("pool_study/check_archive.py",)),
    ("Offline exact pools", ("exact_pool_study/check_archive.py",)),
    ("Index-first development", ("-m", "lazy_cert_study.verify_archive",
        "lazy_cert_study/results/development-v4.jsonl.gz", "--phase", "development")),
    ("Index-first confirmation", ("-m", "lazy_cert_study.verify_archive",
        "lazy_cert_study/results/confirmation.jsonl.gz", "--phase", "confirmation")),
    ("Reviewer audit", ("-m", "reviewer_audit_2026_10_31.check_archive")),
    ("Decision audit", ("-m", "decision_audit_2026_10_31.check_archive")),
    ("UTK adapters", ("-m", "utk_adapter_study.check_archive")),
    ("Graph, correction and neural follow-up", ("-m", "argon_followup_2026_11_01.check_archive")),
    ("Claim consolidation", ("-m", "claims_consolidation_2026_11_01.check_archive")),
    ("Full-domain UTK controls", ("-m", "utk_full_domain_2026_11_01.check_archive")),
    ("November 5 sensitivity and oracle", ("-m", "codex_followup_2026_11_05.verify")),
    ("November 5 graph self-review", ("-m", "self_review_2026_11_05.verify")),
]

# These inventories use repository-root-relative paths, as in their CI jobs.
AUDIT_MANIFESTS = [
    "lazy_cert_study/checksums.sha256",
    "reviewer_audit_2026_10_31/checksums.sha256",
    "decision_audit_2026_10_31/checksums.sha256",
    "utk_adapter_study/checksums.sha256",
    "argon_followup_2026_11_01/checksums.sha256",
    "claims_consolidation_2026_11_01/checksums.sha256",
    "utk_full_domain_2026_11_01/checksums.sha256",
]


def verify_manifest(name):
    count = 0
    for line in (ROOT / name).read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected:
            raise RuntimeError(f"Checksum mismatch in {name}: {relative}")
        count += 1
    print(f"Verified {name}: {count} files", flush=True)


def main():
    if not __debug__:
        raise RuntimeError("Scientific checks require assertions; disable Python optimization.")
    verify_manifest("integration_checksums.sha256")
    for name in AUDIT_MANIFESTS:
        verify_manifest(name)
    for index, (label, arguments) in enumerate(STAGES, 1):
        print(f"[{index}/{len(STAGES)}] Checking {label}", flush=True)
        subprocess.run([sys.executable, *arguments], cwd=ROOT, check=True)
    print(f"PASS: all {len(STAGES)} recorded archive stages verified. "
          "No raw-data download or new benchmark run was performed.", flush=True)

if __name__ == "__main__":
    main()
