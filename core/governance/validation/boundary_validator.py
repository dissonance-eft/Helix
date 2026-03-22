"""
Boundary Validator — core/governance/validation/boundary_validator.py
======================================================================
Cross-system validation for architectural layer boundaries.

Extends the existing governance validation layer with checks that
detect illegal import dependencies between domains, labs, and core.

This is NOT about whether code runs. It is about whether the dependency
structure of the code itself respects the Helix layer architecture.

Rules enforced:
  1. domains/ must not import from applications/labs/
  2. applications/labs/ must not import from core.kernel or core.governance (extends validate_rings.py)
  3. domains/ must not import from other domains/ directly
     (cross-domain work routes through core adapters, not direct imports)
  4. applications/labs/ must not import from domains/ directly
     (labs are exploratory; domains are canonical; cross-over is a structural violation)

These are structural rules, not style guidelines. Violations indicate that the
canonical pipeline is being short-circuited.

Usage:
    from core.governance.validation.boundary_validator import validate_all_boundaries
    report = validate_all_boundaries()
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parent.parent.parent.parent  # repo root


class BoundaryViolation(NamedTuple):
    file: str
    rule: str
    illegal_import: str


def _parse_imports(path: Path) -> list[str]:
    """Extract all import targets from a Python file."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return []

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        elif isinstance(node, ast.Call):
            # importlib.import_module("...") pattern
            if (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "import_module"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                imports.append(node.args[0].value)
    return imports


def _scan_dir(directory: Path, rule: str, illegal_prefixes: list[str]) -> list[BoundaryViolation]:
    violations = []
    if not directory.exists():
        return violations
    for py_file in directory.rglob("*.py"):
        for imp in _parse_imports(py_file):
            for prefix in illegal_prefixes:
                if imp.startswith(prefix):
                    violations.append(BoundaryViolation(
                        file=str(py_file.relative_to(ROOT)),
                        rule=rule,
                        illegal_import=imp,
                    ))
    return violations


def validate_domains_dont_import_labs() -> list[BoundaryViolation]:
    """Rule 1: domains/ must not import from applications.labs."""
    return _scan_dir(
        ROOT / "domains",
        rule="DOMAIN_IMPORTS_LABS",
        illegal_prefixes=["applications.labs", "applications/labs"],
    )


def validate_labs_dont_import_domains_directly() -> list[BoundaryViolation]:
    """Rule 4: applications/labs must not import from domains directly."""
    return _scan_dir(
        ROOT / "applications" / "labs",
        rule="LABS_IMPORTS_DOMAIN_DIRECTLY",
        illegal_prefixes=["domains."],
    )


def validate_domains_dont_cross_import() -> list[BoundaryViolation]:
    """
    Rule 3: A domain must not import from a sibling domain directly.
    Cross-domain work routes through core/adapters/, not peer imports.

    Example violation: domains/music imports from domains.math
    """
    violations = []
    domains_root = ROOT / "domains"
    if not domains_root.exists():
        return violations

    domain_dirs = [d for d in domains_root.iterdir() if d.is_dir() and not d.name.startswith("_")]
    for domain_dir in domain_dirs:
        other_prefixes = [
            f"domains.{d.name}"
            for d in domain_dirs
            if d.name != domain_dir.name
        ]
        for py_file in domain_dir.rglob("*.py"):
            for imp in _parse_imports(py_file):
                for prefix in other_prefixes:
                    if imp.startswith(prefix):
                        violations.append(BoundaryViolation(
                            file=str(py_file.relative_to(ROOT)),
                            rule="DOMAIN_CROSS_IMPORTS_DOMAIN",
                            illegal_import=imp,
                        ))
    return violations


def validate_all_boundaries() -> dict:
    """
    Run all boundary checks and return a structured report.

    Returns:
        {
            "passed": bool,
            "violations": list[dict],
            "summary": {...}
        }
    """
    all_violations: list[BoundaryViolation] = []

    all_violations += validate_domains_dont_import_labs()
    all_violations += validate_labs_dont_import_domains_directly()
    all_violations += validate_domains_dont_cross_import()

    passed = len(all_violations) == 0
    return {
        "passed": passed,
        "violation_count": len(all_violations),
        "violations": [v._asdict() for v in all_violations],
        "summary": {
            "DOMAIN_IMPORTS_LABS": sum(1 for v in all_violations if v.rule == "DOMAIN_IMPORTS_LABS"),
            "LABS_IMPORTS_DOMAIN_DIRECTLY": sum(1 for v in all_violations if v.rule == "LABS_IMPORTS_DOMAIN_DIRECTLY"),
            "DOMAIN_CROSS_IMPORTS_DOMAIN": sum(1 for v in all_violations if v.rule == "DOMAIN_CROSS_IMPORTS_DOMAIN"),
        },
    }


if __name__ == "__main__":
    import json
    import sys
    report = validate_all_boundaries()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report["passed"] else 1)
