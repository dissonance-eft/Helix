"""
Entity Ontology
===============
Single-source entity type definitions for the Helix entity system.

Consumed by:
  core/entities/schema.py  — validation
  core/entities/registry.py — type filtering
  core/hil/ontology.py      — HIL parser entity type recognition
"""
from __future__ import annotations

# Core entity types: fully supported, used by existing substrates
ENTITY_CORE_TYPES: frozenset[str] = frozenset({
    "Composer",
    "Track",
    "Game",
    "Platform",
    "SoundChip",
    "SoundTeam",
})

# Reserved entity types: defined in ontology but not yet required by active substrates
ENTITY_RESERVED_TYPES: frozenset[str] = frozenset({
    "Soundtrack",
    "Studio",
    "Dataset",
    "Experiment",
    "Model",
    "Invariant",
    "Operator",
})

# Full ontology: all recognized entity types
ENTITY_ONTOLOGY: frozenset[str] = ENTITY_CORE_TYPES | ENTITY_RESERVED_TYPES


def is_core_entity_type(type_str: str) -> bool:
    return type_str in ENTITY_CORE_TYPES


def is_reserved_entity_type(type_str: str) -> bool:
    return type_str in ENTITY_RESERVED_TYPES


def is_known_entity_type(type_str: str) -> bool:
    return type_str in ENTITY_ONTOLOGY
