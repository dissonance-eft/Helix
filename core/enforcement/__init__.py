"""
Helix Enforcement — Final MISSING LAYER
=======================================
Centralized enforcement authority for the Helix repository.
This layer maintains the architectural integrity of the system
at runtime by preventing illegal states and layer violations.
"""
from core.enforcement.failure_states import FAILURE_STATES, Severity
from core.enforcement.rules import Law, Layer, LAYER_PATHS
from core.enforcement.validators import (
    validate_id,
    validate_entity_schema,
    EnforcementError,
    ValidationError,
    IDError
)
from core.enforcement.runtime_checks import (
    authorize_atlas_write,
    pre_persistence_check,
    enforce_persistence,
    IllegalWriteError,
    LayerViolationError
)
from core.enforcement.audit import audit_system_state

__all__ = [
    "FAILURE_STATES", "Severity",
    "Law", "Layer", "LAYER_PATHS",
    "validate_id", "validate_entity_schema", 
    "EnforcementError", "ValidationError", "IDError",
    "authorize_atlas_write", "pre_persistence_check", "enforce_persistence",
    "IllegalWriteError", "LayerViolationError",
    "audit_system_state"
]
