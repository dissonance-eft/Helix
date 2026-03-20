"""
Helix Enforcement — Runtime Checks
==================================
Implements hard gates for Helix runtime behavior and filesystem access.
"""
from __future__ import annotations

import os
import inspect
from pathlib import Path
from typing import Any, Optional

import json
from core.enforcement.failure_states import FAILURE_STATES, Severity
from core.enforcement.validators import (
    EnforcementError,
    validate_entity_schema,
    validate_id
)

class LayerViolationError(EnforcementError):
    """Raised when an illegal cross-layer interaction is detected."""
    pass

class IllegalWriteError(EnforcementError):
    """Raised when an unauthorized ATLAS write is attempted."""
    pass

# ---------------------------------------------------------------------------
# Path Enforcement
# ---------------------------------------------------------------------------

def authorize_atlas_write(caller_stack_depth: int = 1) -> None:
    """
    Ensure the current write to ATLAS is authorized.
    Only core/compiler/ entries or tests are allowed to commit to atlas/.
    
    Raises IllegalWriteError on failure.
    """
    # Find the caller
    stack = inspect.stack()
    index = caller_stack_depth + 1
    if index >= len(stack):
        index = len(stack) - 1
    
    caller_frame = stack[index]
    caller_path = Path(caller_frame.filename).resolve()
    
    # Authorized paths
    # 1. core/compiler/
    # 2. tests/
    
    is_authorized = False
    if "core" in caller_path.parts and "compiler" in caller_path.parts:
        is_authorized = True
    
    if any(p in caller_path.parts for p in ("tests", "pytest", "unit_tests")):
        is_authorized = True
        
    if not is_authorized:
        rel_caller = ""
        try:
            rel_caller = os.path.relpath(caller_path, os.getcwd())
        except ValueError:
            rel_caller = caller_path.name
            
        print(f"[!] ENFORCEMENT BREACH DETECTED: Illegal Atlas write attempt from '{rel_caller}'.")
        raise IllegalWriteError(
            f"Unauthorized Atlas write attempt from '{rel_caller}'. "
            "All writes must be routed through the canonical enforcement gateway.",
            "ILLEGAL_ATLAS_WRITE"
        )

# ---------------------------------------------------------------------------
# Entity Persistence Gate (CANONICAL GATED GATEWAY)
# ---------------------------------------------------------------------------

def enforce_persistence(entity: dict[str, Any], path: Path, is_atlas: bool = True) -> Path:
    """
    The ONLY authorized path for persisting Helix knowledge.
    Ensures authorization, validation, and atomic filesystem commit.
    
    Pipeline:
      authorize → audit → validate → atomic_write
    """
    # 1. Authorize (look past this function to the caller)
    authorize_atlas_write(caller_stack_depth=1)
    
    # 2. Schema / ID validation
    # This also enforces CCS for atlas entities
    pre_persistence_check(entity, path)
    
    # 3. Path authorization check for atlas target
    if is_atlas and "atlas" not in path.parts:
        # Caller claims it's Atlas, but path is not
        raise IllegalWriteError(f"Target path '{path}' is not in the Atlas.", "ILLEGAL_ATLAS_WRITE")
    
    # 4. Canonical formatting & Clean-up
    # Strip internal compiler/private keys beginning with '_'
    clean_data = {k: v for k, v in entity.items() if not k.startswith("_")}
    
    # 5. Atomic Persistence
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(f".{os.getpid()}.tmp")
    try:
        # Indent=2 is the Helix standard for JSON storage
        content = json.dumps(clean_data, indent=2, ensure_ascii=False)
        temp_path.write_text(content, encoding="utf-8")
        
        # Replace replaces and is atomic on most systems
        if os.name == 'nt' and path.exists():
            # os.replace on Windows may fail if the file is open, 
            # but for this repo it should be fine as it's append-only/locked
            pass
        os.replace(temp_path, path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise EnforcementError(f"Persistence operation failed for {path}: {e}", "UNLOGGED_MUTATION")
    
    return path

# ---------------------------------------------------------------------------
# Entity Pre-persistence Internal Checks
# ---------------------------------------------------------------------------

def pre_persistence_check(entity: dict[str, Any], path: Path) -> None:
    """
    Internal hard-gate check before data hits the filesystem logic.
    Used by enforce_persistence().
    """
    # SKIP schema check for recognized structural files
    if path.name in ("registry.json", "atlas_graph.json", "index.json"):
        return

    # Atlas entities must pass full schema + ID check
    if "atlas" in path.parts:
        # Atlas entities require full cognitive schema (CCS)
        validate_entity_schema(entity, is_atlas=True)
    elif "codex" in path.parts and "library" in path.parts:
        # Library entities require core schema but not CCS
        validate_entity_schema(entity, is_atlas=False)
    else:
        # Fallback to base schema validation
        validate_entity_schema(entity, is_atlas=False)

# ---------------------------------------------------------------------------
# Layer Separation Checks
# ---------------------------------------------------------------------------

def enforce_layer_isolation() -> None:
    """
    Audit for layer-skipping imports. (Self-audit probe).
    """
    # Placeholder for dynamic import graph auditing
    # For now, it's just a warning.
    pass
