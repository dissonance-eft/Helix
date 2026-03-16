"""
Filesystem Probe — Helix Phase 9
Verifies that the Helix filesystem is real and persistent across
sequential operations.

Creates a sentinel file with a random name, then verifies it persists
after a subsequent read operation. If the file disappears between
writes and reads, the filesystem is not persistent (simulated context).
"""

from __future__ import annotations
import os
import uuid
from dataclasses import dataclass
from pathlib import Path


SENTINEL_DIR = Path(__file__).parent.parent.parent / "artifacts" / "_integrity"


@dataclass
class FilesystemResult:
    passed:        bool
    sentinel_path: str
    details:       str


def probe() -> FilesystemResult:
    SENTINEL_DIR.mkdir(parents=True, exist_ok=True)
    sentinel = SENTINEL_DIR / f"helix_integrity_{uuid.uuid4().hex[:12]}.txt"

    try:
        # Write
        payload = f"helix-integrity-check:{uuid.uuid4()}"
        sentinel.write_text(payload)

        # Verify existence after write
        if not sentinel.exists():
            return FilesystemResult(
                passed=False,
                sentinel_path=str(sentinel),
                details="Sentinel file does not exist immediately after write.",
            )

        # Verify content persists across a subsequent read
        read_back = sentinel.read_text()
        if read_back != payload:
            return FilesystemResult(
                passed=False,
                sentinel_path=str(sentinel),
                details=f"Content mismatch. Written: {payload!r}, Read: {read_back!r}",
            )

        # Clean up
        sentinel.unlink()
        return FilesystemResult(
            passed=True,
            sentinel_path=str(sentinel),
            details="Sentinel created, persisted, read back correctly, and cleaned up.",
        )

    except Exception as e:
        return FilesystemResult(
            passed=False,
            sentinel_path=str(sentinel),
            details=f"Filesystem probe error: {e}",
        )


if __name__ == "__main__":
    r = probe()
    print(f"[{'PASS' if r.passed else 'FAIL'}] filesystem_probe")
    print(f"  Sentinel: {r.sentinel_path}")
    print(f"  Details:  {r.details}")
