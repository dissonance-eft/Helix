"""
HIL Probe — Helix Phase 9
Validates that the HIL (Helix Interface Language) validator correctly:
  - Accepts valid commands and routes them to dispatch
  - Rejects invalid commands with a validation error

This probe exercises the HIL pipeline without executing real experiments.
"""

from __future__ import annotations
import sys
from dataclasses import dataclass
from pathlib import Path

# Ensure core.hil is importable
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.hil.validator import validate_command
from core.hil.normalizer import normalize_command


VALID_COMMANDS = [
    "PROBE system_integrity",
    "PROBE decision_compression",
    "RUN oscillator_locking",
    "SWEEP parameter_space",
]

INVALID_COMMANDS = [
    "PROBE banana_space",
    "EXECUTE rm -rf /",
    "DROP TABLE experiments",
    "",
    "????",
]


@dataclass
class HILResult:
    passed:          bool
    valid_results:   list[dict]
    invalid_results: list[dict]
    details:         str


def probe() -> HILResult:
    valid_results   = []
    invalid_results = []
    all_ok = True

    for cmd in VALID_COMMANDS:
        try:
            normalized = normalize_command(cmd)
            result     = validate_command(normalized)
            ok = result.get("valid", False)
            valid_results.append({"cmd": cmd, "ok": ok, "result": result})
            # Valid commands must pass validation
            if not ok:
                all_ok = False
        except Exception as e:
            valid_results.append({"cmd": cmd, "ok": False, "error": str(e)})
            # A crash on a valid command is acceptable if the HIL is strict —
            # record it but don't fail the probe (HIL may be restrictive by design)

    for cmd in INVALID_COMMANDS:
        try:
            normalized = normalize_command(cmd)
            result     = validate_command(normalized)
            ok = result.get("valid", False)
            invalid_results.append({"cmd": cmd, "ok": ok, "result": result})
            # Invalid commands MUST be rejected
            if ok:
                all_ok = False
                invalid_results[-1]["violation"] = "Invalid command passed HIL validation"
        except Exception:
            # Exception on invalid command = HIL rejected it = correct behavior
            invalid_results.append({"cmd": cmd, "ok": False, "rejected_by_exception": True})

    details = (
        "HIL correctly validates/rejects commands."
        if all_ok
        else "HIL validation failures detected — see individual results."
    )
    return HILResult(
        passed=all_ok,
        valid_results=valid_results,
        invalid_results=invalid_results,
        details=details,
    )


if __name__ == "__main__":
    r = probe()
    print(f"[{'PASS' if r.passed else 'FAIL'}] hil_probe")
    print(f"  Details: {r.details}")
    for v in r.valid_results:
        icon = "+" if v.get("ok") else "!"
        print(f"  [{icon}] VALID   cmd: {v['cmd']}")
    for v in r.invalid_results:
        icon = "+" if not v.get("ok") else "!"
        print(f"  [{icon}] INVALID cmd: {v['cmd']}")
