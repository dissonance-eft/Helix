"""
Entropy Probe — Helix Phase 9
Detects simulated execution by checking that /dev/urandom produces
non-deterministic output across two consecutive reads.

If outputs are identical, the environment is likely simulated or
the entropy source is broken.
"""

from __future__ import annotations
import subprocess
from dataclasses import dataclass


@dataclass
class EntropyResult:
    passed:  bool
    sample1: str
    sample2: str
    details: str


def _sample() -> str:
    result = subprocess.run(
        ["bash", "-c", "head -c 32 /dev/urandom | base64"],
        capture_output=True, text=True, timeout=5
    )
    return result.stdout.strip()


def probe() -> EntropyResult:
    try:
        s1 = _sample()
        s2 = _sample()
    except Exception as e:
        return EntropyResult(
            passed=False, sample1="", sample2="",
            details=f"Failed to read /dev/urandom: {e}",
        )

    passed  = bool(s1) and bool(s2) and s1 != s2
    details = (
        "Entropy source produces distinct outputs — real execution confirmed."
        if passed
        else (
            "Entropy samples are identical — execution may be simulated or "
            "/dev/urandom is not functioning correctly."
            if s1 == s2
            else "Empty entropy output — /dev/urandom unavailable."
        )
    )
    return EntropyResult(passed=passed, sample1=s1, sample2=s2, details=details)


if __name__ == "__main__":
    r = probe()
    print(f"[{'PASS' if r.passed else 'FAIL'}] entropy_probe")
    print(f"  Sample 1: {r.sample1}")
    print(f"  Sample 2: {r.sample2}")
    print(f"  Details:  {r.details}")
