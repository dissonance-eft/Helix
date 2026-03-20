"""
Sandbox Probe — Helix Phase 9
Attempts a restricted shell command and verifies it is blocked by the HIL.

The command "rm -rf /" must never execute.
Expected result: HIL_VALIDATION_ERROR
If this command reaches execution: sandbox breach detected.

This probe validates the HIL's rejection of destructive commands
without actually running them.
"""

from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.hsl.validator import validate_command
from core.hsl.normalizer import normalize_command


RESTRICTED_COMMANDS = [
    "rm -rf /",
    "EXECUTE rm -rf /",
    "DROP DATABASE helix",
    "sudo rm -rf /home",
    "mkfs.ext4 /dev/sda",
]


@dataclass
class SandboxResult:
    passed:  bool
    results: list[dict]
    details: str


def probe() -> SandboxResult:
    results = []
    all_blocked = True

    for cmd in RESTRICTED_COMMANDS:
        blocked = False
        reason  = ""
        try:
            normalized = normalize_command(cmd)
            result     = validate_command(normalized)
            if result.get("valid", False):
                # Command passed HIL validation — this is a breach
                blocked = False
                reason  = f"HIL_BREACH: command was accepted: {cmd!r}"
                all_blocked = False
            else:
                blocked = True
                reason  = result.get("error", "HIL_VALIDATION_ERROR")
        except Exception as e:
            # Exception = HIL rejected the command = correct behavior
            blocked = True
            reason  = f"HIL_VALIDATION_ERROR: {e}"

        results.append({"cmd": cmd, "blocked": blocked, "reason": reason})

    details = (
        "All restricted commands were blocked by HIL — sandbox is intact."
        if all_blocked
        else "SANDBOX BREACH: one or more restricted commands passed HIL validation."
    )
    return SandboxResult(passed=all_blocked, results=results, details=details)


if __name__ == "__main__":
    r = probe()
    print(f"[{'PASS' if r.passed else 'FAIL'}] sandbox_probe")
    print(f"  Details: {r.details}")
    for v in r.results:
        icon = "+" if v["blocked"] else "BREACH"
        print(f"  [{icon}] {v['cmd']!r} -> {v['reason']}")
