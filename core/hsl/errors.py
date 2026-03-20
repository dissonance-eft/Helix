"""
HIL Error Hierarchy
===================
Structured error classes for the Helix Interface Language.
Parser errors and validator errors are always distinct.
"""
from __future__ import annotations


class HSLError(Exception):
    """Base class for all HSL errors."""

    def __init__(self, message: str, raw: str = "", position: int = -1, suggestion: str = None):
        super().__init__(message)
        self.raw      = raw
        self.position = position
        self.suggestion = suggestion

    def to_dict(self) -> dict:
        d = {
            "error_type": type(self).__name__,
            "message":    str(self),
            "raw":        self.raw,
            "position":   self.position,
        }
        if self.suggestion:
            d["suggestion"] = self.suggestion
        return d


class HSLSyntaxError(HSLError):
    """Tokenizer or parser failed to parse the raw input."""


class HSLValidationError(HSLError):
    """Parsed command failed semantic validation."""


class HSLUnknownCommandError(HSLError):
    """Verb is not registered in the HSL command registry."""


class HSLUnknownTargetError(HSLError):
    """Typed reference names an object not present in the atlas registry."""


class HSLUnsafeCommandError(HSLError):
    """Command contains a pattern blocked by the HSL safety policy."""


class HSLAmbiguityError(HSLError):
    """Alias expansion is ambiguous — multiple valid expansions exist."""
