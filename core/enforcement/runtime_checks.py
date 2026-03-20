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

from core.enforcement.failure_states import FAILURE_STATES, Severity
from core.enforcement.validators import EnforcementError, validate_entity_schema

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
    Only core/compiler/ entries are allowed to commit to atlas/.
    
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
    # 1. core/compiler/atlas_compiler.py
    # 2. core/compiler/registry_writer.py
    # 3. core/compiler/atlas_generator.py
    
    is_authorized = False
    if "core" in caller_path.parts and "compiler" in caller_path.parts:
        is_authorized = True
    
    # Also allow tests (if running within a test suite)
    if any(p in caller_path.parts for p in ("tests", "pytest", "unit_tests")):
        is_authorized = True
        
    if not is_authorized:
        rel_caller = caller_path.name
        try:
            rel_caller = os.path.relpath(caller_path, os.getcwd())
        except ValueError:
            pass
            
        raise IllegalWriteError(
            f"Unauthorized Atlas write attempt from '{rel_caller}'. "
            "All writes must be routed through core.compiler.atlas_compiler.",
            "ILLEGAL_ATLAS_WRITE"
        )

# ---------------------------------------------------------------------------
# Entity Persistence Checks
# ---------------------------------------------------------------------------

def pre_persistence_check(entity: dict[str, Any], path: Path) -> None:
    """
    Final hard-gate check before any data is written to disk.
    
    1. Validates schema
    2. Validates ID
    3. Authorizes based on target path
    
    Raises EnforcementError on any violation.
    """
    # 1. Authorize path-based access
    if "atlas" in path.parts:
        # Atlas writes require compiler-only access
        authorize_atlas_write(caller_stack_depth=1)
        # Atlas entities require full cognitive schema
        validate_entity_schema(entity, is_atlas=True)
    elif "codex" in path.parts and "library" in path.parts:
        # Library entities require core schema but not CCS embedding
        validate_entity_schema(entity, is_atlas=False)
    else:
        # Generic entities
        validate_entity_schema(entity, is_atlas=False)

# ---------------------------------------------------------------------------
# Layer Separation Checks
# ---------------------------------------------------------------------------

def enforce_layer_isolation() -> None:
    """
    Dynamic check to ensure applications aren't importing or calling 
    low-level mutable state directly.
    
    Note: High overhead if called frequently. Recommended as probe or
    pipeline initialization step.
    """
    # Placeholder for dynamic import graph auditing
    # For now, it's just a warning.
    pass
