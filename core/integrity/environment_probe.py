"""
Environment Probe — Helix Phase 9
Verifies Helix is running inside a real WSL2 environment.

Checks /proc/version for the WSL2 kernel signature.
Failure means the execution environment is not what is expected
(simulated, wrong OS, CI runner without WSL, etc.)
"""

from __future__ import annotations
import subprocess
from dataclasses import dataclass
from pathlib import Path


WSL_SIGNATURE = "microsoft-standard-WSL2"
PROC_VERSION  = Path("/proc/version")


@dataclass
class EnvironmentResult:
    passed:    bool
    signature: str
    details:   str


def probe() -> EnvironmentResult:
    # Primary check: /proc/version
    if PROC_VERSION.exists():
        version = PROC_VERSION.read_text().strip()
    else:
        # Fallback: uname -r
        try:
            version = subprocess.check_output(
                ["uname", "-r"], text=True, timeout=5
            ).strip()
        except Exception as e:
            return EnvironmentResult(
                passed=False,
                signature="UNAVAILABLE",
                details=f"Could not read kernel version: {e}",
            )

    passed  = WSL_SIGNATURE.lower() in version.lower()
    details = (
        "WSL2 kernel signature confirmed."
        if passed
        else f"Expected '{WSL_SIGNATURE}' in kernel string. Got: {version[:120]}"
    )
    return EnvironmentResult(passed=passed, signature=version[:120], details=details)


if __name__ == "__main__":
    r = probe()
    print(f"[{'PASS' if r.passed else 'FAIL'}] environment_probe")
    print(f"  Signature: {r.signature}")
    print(f"  Details:   {r.details}")
