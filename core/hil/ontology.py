"""
HIL Ontology
============
Object type categories recognised by HIL.
Legal type prefixes for typed references: prefix:name

Entity types (SPEC-02) are maintained in core/entities/ontology.py and
re-exported here so the HIL parser has a single import path.
"""
from __future__ import annotations

from core.kernel.schema.entities.ontology import (
    ENTITY_CORE_TYPES,
    ENTITY_RESERVED_TYPES,
    ENTITY_ONTOLOGY,
    is_known_entity_type as _is_known_entity_type,
)

OBJECT_TYPES: frozenset[str] = frozenset({
    "invariant", "experiment", "model", "regime", "operator",
    "artifact", "engine", "parameter", "atlas", "graph",
    "atlas_entry", "graph_query",
    "music", "track", "composer", "soundtrack", "sound_team", "platform", "sound_chip", "domain",
    "substrate", "pipeline", "dataset", "roadmap_entry", "application", "entity"
})

ATLAS_BACKED_TYPES: frozenset[str] = frozenset({
    "invariant", "experiment", "model", "regime", "operator",
})

VALID_ENGINES: frozenset[str] = frozenset({"python", "godot"})

FREE_PARAM_TYPES: frozenset[str] = frozenset({
    "parameter", "artifact", "atlas", "graph", "atlas_entry", "graph_query",
})

_PLURAL: dict[str, str] = {
    "invariant":  "invariants",
    "experiment": "experiments",
    "model":      "models",
    "regime":     "regimes",
    "operator":   "operators",
}


def is_valid_type(prefix: str) -> bool:
    return prefix in OBJECT_TYPES

def is_atlas_backed(prefix: str) -> bool:
    return prefix in ATLAS_BACKED_TYPES

def is_free_param(prefix: str) -> bool:
    return prefix in FREE_PARAM_TYPES

def plural_key(prefix: str) -> str:
    """Return the atlas_index.yaml section key for this type prefix."""
    return _PLURAL.get(prefix, prefix + "s")

def is_entity_type(prefix: str) -> bool:
    """Return True if prefix (case-insensitive) matches a known entity type.

    Handles both simple-capitalized types ('composer' → 'Composer') and
    compound types ('soundchip' → 'SoundChip', 'sound_chip' → 'SoundChip').
    """
    # Build a lowercase→canonical lookup once (cached at module level below)
    return prefix.lower().replace("_", "") in _ENTITY_TYPE_LOWER_MAP


# Lowercase-stripped lookup: "soundchip" → "SoundChip", "composer" → "Composer"
_ENTITY_TYPE_LOWER_MAP: frozenset[str] = frozenset(
    t.lower().replace("_", "") for t in ENTITY_ONTOLOGY
)
