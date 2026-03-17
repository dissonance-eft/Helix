"""
HIL Semantic Roles
==================
Relationship types between atlas objects.
Scaffolded here for graph-query readiness; consumed by Atlas graph edges.

Design note (case-language influence):
  Roles act like grammatical cases: they mark the relation between
  objects explicitly rather than relying on word order.
"""
from __future__ import annotations
from enum import Enum


class SemanticRole(str, Enum):
    """First-class relation types used in HIL commands and Atlas graph edges."""
    SUPPORTS       = "supports"
    CONTRADICTS    = "contradicts"
    DERIVES_FROM   = "derives_from"
    EMERGES_FROM   = "emerges_from"
    TRANSITIONS_TO = "transitions_to"
    TESTS          = "tests"
    IMPLEMENTS     = "implements"
    REFERENCES     = "references"
    TRACES         = "traces"
    COMPOSED       = "composed"
    MEMBER_OF      = "member_of"
    APPEARS_IN     = "appears_in"
    USES_CHIP      = "uses_chip"
    COLLABORATED_WITH = "collaborated_with"


COMMAND_ROLE_MAP: dict[str, SemanticRole] = {
    "support":           SemanticRole.SUPPORTS,
    "trace":             SemanticRole.TRACES,
    "derives":           SemanticRole.DERIVES_FROM,
    "implements":        SemanticRole.IMPLEMENTS,
    "tests":             SemanticRole.TESTS,
    "contradicts":       SemanticRole.CONTRADICTS,
    "emerges":           SemanticRole.EMERGES_FROM,
    "composed":          SemanticRole.COMPOSED,
    "member_of":         SemanticRole.MEMBER_OF,
    "appears_in":        SemanticRole.APPEARS_IN,
    "uses_chip":         SemanticRole.USES_CHIP,
    "collaborated_with": SemanticRole.COLLABORATED_WITH,
}


def role_for_command(verb: str, subcommand: str | None = None) -> SemanticRole | None:
    """Return the semantic role expressed by this command, if any."""
    key = (subcommand or verb).lower()
    return COMMAND_ROLE_MAP.get(key)
