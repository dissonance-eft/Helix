"""
Root Guard -- Helix Phase 9
===========================
Enforces that no file is written to the repo root at runtime.

Only these files are permitted at the repo root:
  HELIX.md
  OPERATOR.md

All other paths must resolve inside a registered subdirectory.

Usage:
  from core.kernel.infra.root_guard import assert_not_root
  assert_not_root(path)  # raises RootViolation if path is at root
"""

from __future__ import annotations
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent.parent

ROOT_ALLOWLIST = frozenset({
    "HELIX.md",
    "OPERATOR.md",
    ".gitignore",
    ".git",
})

REGISTERED_DIRS = frozenset({
    "core", "engines", "labs", "atlas", "applications",
    "artifacts", "compiler",
})


class RootViolation(Exception):
    pass


def assert_not_root(path) -> None:
    """Raise RootViolation if path resolves to the repo root level."""
    p = Path(path).resolve()
    try:
        rel = p.relative_to(REPO_ROOT)
    except ValueError:
        return  # outside repo — not our concern
    parts = rel.parts
    if len(parts) == 1 and parts[0] not in ROOT_ALLOWLIST:
        raise RootViolation(
            f"Root lock violation: '{parts[0]}' may not be written to repo root.\n"
            f"Allowed root files: {sorted(ROOT_ALLOWLIST)}\n"
            f"Place it inside: {sorted(REGISTERED_DIRS)}"
        )


def safe_write(path, content: str) -> Path:
    """Write content to path after confirming it is not in the repo root."""
    p = Path(path)
    assert_not_root(p)
    p.write_text(content)
    return p
