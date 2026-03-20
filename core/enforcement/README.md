# Helix Enforcement: System Law

This directory contains the central enforcement authority for the Helix repository. It transforms the architectural philosophy of the system into explicit, machine-enforced runtime guarantees.

## Authoritative Laws

Helix is a governed system. All operations must comply with these laws or fail immediately.

### 1. Layer Separation Laws
- **Immutable Codex**: The `core` may not depend on the `codex/atlas` as a mutable source.
- **Unauthorized Writes**: `applications` may not write to the `atlas/` directly. 
- **Compiler Authority**: All persistent state changes to the Atlas must flow through the central compiler (`core/compiler/atlas_compiler.py`).

### 2. Identity Laws
- **Deterministic Existence**: All persisted knowledge objects must possess a deterministic, unique ID.
- **Canonical Format**: IDs MUST follow the `domain.type:slug` pattern (lowercase, underscores, and digits only).
- **ID Integrity**: Missing or malformed IDs are treated as critical system failures.

### 3. Schema Laws
- **Full Validation**: Every entity written to the Atlas or Library must pass structural and semantic validation against the canonical schema specified in `docs/ENTITY_SCHEMA.md`.
- **Mandatory Provenance**: Entities must include `entity_id`, `entity_type`, `created_at`, and `source`.
- **Cognitive Embedding**: Atlas entities must includes a 6-axis CSS (Cognitive Coordinate System) embedding.

### 4. Relationship Laws
- **Explicit Linkage**: Implicit relationships are forbidden. All graph links must be explicitly declared in the entity schema.
- **Link Validity**: A link is only valid if the target ID is canonical.

### 5. Mutation Laws
- **Observability**: Hidden mutations are illegal. Every architectural transformation must be logged in metadata.
- **Pre-Commit Gate**: No entity may be committed to persistence without passing the `pre_persistence_check`.

## Failure States

Helix defines failure explicitly via the `FailureState` registry in `failure_states.py`. Violations trigger immediate system halt (exceptions) or isolated logging depending on the configured severity.

| Code | Severity | Context |
| :--- | :--- | :--- |
| `INVALID_SCHEMA` | HIGH | Critical metadata missing or malformed data types. |
| `INVALID_ID` | HIGH | Illegal characters or structure in entity identifier. |
| `CROSS_LAYER_VIOLATION` | CRITICAL | Unauthorized cross-layer dependency or write. |
| `ILLEGAL_ATLAS_WRITE` | CRITICAL | Attempted direct filesystem mutation of atlas/. |

## Integration

The enforcement layer is integrated as a hard gate within the `core.compiler.atlas_compiler.atlas_commit` and `core.compiler.registry_writer.write_registry` pipelines.

```python
from core.enforcement import pre_persistence_check

def commit(entity, path):
    # This call will raise EnforcementError if any law is violated
    pre_persistence_check(entity, path)
    path.write_text(json.dumps(entity))
```
