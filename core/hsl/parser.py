"""
HSL Parser
==========
Tokenizer + recursive-descent parser -> HSLCommand AST.

Design influences:
  - Lisp: AST-first, explicit structure, minimal primitives
  - Protocol design: every token has a defined role before dispatch
  - Unix: explicit failure on invalid input, no silent coercion

Token types:
  TYPED_REF   [namespace.]prefix:name   e.g. invariant:decision_compression
                                             music.composer:jun_senoue
  RANGE       low..high                 e.g. 0..1
  NUMBER      integer or float
  WORD        bare identifier           (valid only as verb or subcommand)
  WHITESPACE  skipped

Grammar sketch:
  command    = verb [subcommand] {typed-ref | param}
  verb       = WORD (must be in VALID_VERBS)
  subcommand = WORD (only if spec.requires_subcommand or spec has subcommands)
  typed-ref  = TYPED_REF where type-prefix in OBJECT_TYPES or entity ontology
  param      = TYPED_REF where prefix in {range, engine, steps, seed, ...}
"""
from __future__ import annotations

import re
from typing import Any

from core.hsl.ast_nodes import HSLCommand, TypedRef, RangeExpr
from core.hsl.errors import (
    HSLSyntaxError, HSLUnknownCommandError, HSLUnsafeCommandError,
)
from core.hsl.ontology import OBJECT_TYPES, is_entity_type
from core.hsl.command_registry import VALID_VERBS, get_spec

# ── Safety patterns rejected before tokenization ──────────────────────────────
_BLOCKED_RAW: tuple[str, ...] = (
    "rm ", "rm\t", "mkfs", "dd ", "dd\t", "sudo ",
    "DROP ", "DELETE FROM", "> /dev/",
    "chmod ", "chown ", "wget ", "curl ",
    "exec(", "__import__", "os.system", "subprocess",
    "eval(", "fork()", ">>",
)

# ── Tokenizer ─────────────────────────────────────────────────────────────────
_TOKEN_PATTERNS: list[tuple[str, str]] = [
    # Support optional namespace prefix: [namespace.]prefix:value
    # e.g. invariant:decision_compression  or  music.composer:jun_senoue
    # Also supports prefix:"quoted value" or prefix:unquoted_value
    # Value may start with a digit (e.g. stages:3,4,5 or track:01_angel)
    ("TYPED_REF", r'[a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)?:(?:"[^"]*"|\'[^\']*\'|[a-zA-Z0-9_][a-zA-Z0-9_.\-,:]*)'),
    # key=value style params (alternative to key:value)
    ("PARAM_EQ",  r'[a-zA-Z_][a-zA-Z0-9_]*=(?:"[^"]*"|\'[^\']*\'|[^\s]+)'),
    ("RANGE",     r"\d+(?:\.\d+)?\.\.\d+(?:\.\d+)?"),
    ("NUMBER",    r"\d+(?:\.\d+)?"),
    ("WORD",      r"[a-zA-Z_][a-zA-Z0-9_\-]*"),
    ("WS",        r"\s+"),
    ("UNKNOWN",   r"."),
]
_TOKEN_RE = re.compile(
    "|".join(f"(?P<{n}>{p})" for n, p in _TOKEN_PATTERNS)
)


def _tokenize(text: str) -> list[tuple[str, str]]:
    tokens: list[tuple[str, str]] = []
    for m in _TOKEN_RE.finditer(text):
        kind = m.lastgroup
        if kind == "WS":
            continue
        if kind == "UNKNOWN":
            raise HSLSyntaxError(
                f"Unexpected character {m.group()!r} at position {m.start()}",
                raw=text, position=m.start(),
            )
        tokens.append((kind, m.group()))
    return tokens


# ── Range parsing ─────────────────────────────────────────────────────────────

def _parse_range(s: str, raw: str) -> RangeExpr:
    if ".." not in s:
        raise HSLSyntaxError(f"Invalid range {s!r}: expected low..high", raw=raw)
    left, _, right = s.partition("..")
    try:
        lo, hi = float(left), float(right)
    except ValueError:
        raise HSLSyntaxError(
            f"Range bounds must be numbers, got {s!r}", raw=raw
        )
    if lo > hi:
        raise HSLSyntaxError(
            f"Range low ({lo}) must be <= high ({hi})", raw=raw
        )
    return RangeExpr(lo, hi)


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9_]", "_", s.lower()).strip("_")


# ── Parser ────────────────────────────────────────────────────────────────────

def parse(raw: str) -> HSLCommand:
    """
    Parse raw HSL string -> HSLCommand AST.
    Raises HSLSyntaxError, HSLUnknownCommandError, or HSLUnsafeCommandError.
    """
    text = raw.strip()
    if not text:
        raise HSLSyntaxError("Empty command", raw=raw)

    # Shell command interception
    shell_suggestions = {
        "dir": "SCAN filesystem path:\"...\"",
        "ls": "SCAN filesystem path:\"...\"",
        "get-childitem": "SCAN filesystem path:\"...\"",
        "cmd": "Use HIL operators for system tasks",
        "powershell": "Use HIL operators for system tasks",
        "bash": "Use HIL operators for system tasks",
    }

    text_lower = text.lower()
    first_word = text_lower.split()[0] if text_lower.split() else ""
    if first_word in shell_suggestions:
        raise HSLUnsafeCommandError(
            f"Direct shell command {first_word!r} is not permitted in Helix.",
            raw=raw,
            suggestion=f"Use HIL operator instead → {shell_suggestions[first_word]}"
        )

    # Safety: reject blocked patterns before tokenization
    for pat in _BLOCKED_RAW:
        stripped = pat.strip()
        # For patterns that are likely commands (short, alphabetic), use strict word boundaries.
        if stripped.isalpha() and len(stripped) <= 5:
            if re.search(rf"\b{re.escape(stripped)}\b", text_lower):
                raise HSLUnsafeCommandError(
                    f"Blocked pattern detected: {stripped!r}", raw=raw
                )
        # For mult-word or symbolic patterns, check for direct inclusion.
        elif len(stripped) > 5 or not stripped.isalpha():
            if stripped.lower() in text_lower:
                raise HSLUnsafeCommandError(
                    f"Blocked pattern detected: {stripped!r}", raw=raw
                )

    try:
        tokens = _tokenize(text)
    except HSLSyntaxError:
        raise
    except Exception as e:
        raise HSLSyntaxError(str(e), raw=raw) from e

    if not tokens:
        raise HSLSyntaxError("No tokens found", raw=raw)

    pos = 0

    def peek() -> tuple[str, str] | None:
        return tokens[pos] if pos < len(tokens) else None

    def consume() -> tuple[str, str]:
        nonlocal pos
        if pos >= len(tokens):
            raise HSLSyntaxError("Unexpected end of input", raw=raw)
        tok = tokens[pos]
        pos += 1
        return tok

    # ── Verb ──────────────────────────────────────────────────────────────
    kind, val = consume()
    if kind != "WORD":
        raise HSLSyntaxError(
            f"Command must begin with a verb, got {val!r}", raw=raw, position=0
        )
    verb = val.upper()
    if verb not in VALID_VERBS:
        raise HSLUnknownCommandError(f"Unknown verb: {val!r}", raw=raw)

    spec = get_spec(verb)
    subcommand: str | None = None
    targets: list[TypedRef] = []
    params: dict[str, Any] = {}

    # ── Subcommand ────────────────────────────────────────────────────────
    if spec.requires_subcommand():
        if not peek() or peek()[0] != "WORD":
            raise HSLSyntaxError(
                f"{verb} requires a subcommand, one of: {sorted(spec.subcommands)}",
                raw=raw,
            )
        _, sub_val = consume()
        subcommand = sub_val.lower()
    elif spec.has_subcommands() and peek() and peek()[0] == "WORD":
        # Optional subcommand: consume if it matches a known subcommand
        _, sub_val = peek()
        if sub_val.lower() in {s.lower() for s in spec.subcommands}:
            consume()
            subcommand = sub_val.lower()

    # ── Targets and params ────────────────────────────────────────────────
    while pos < len(tokens):
        kind, val = peek()

        if kind == "TYPED_REF":
            consume()
            colon = val.index(":")
            full_prefix = val[:colon].lower()
            name        = val[colon + 1:]

            # Unquote if necessary
            if (name.startswith('"') and name.endswith('"')) or \
               (name.startswith("'") and name.endswith("'")):
                name = name[1:-1]

            # Split optional namespace: "music.composer" → ("music", "composer")
            if "." in full_prefix:
                namespace, type_prefix = full_prefix.split(".", 1)
            else:
                namespace, type_prefix = "", full_prefix

            if type_prefix == "range":
                params["range"] = _parse_range(name, raw)
            elif type_prefix == "engine":
                params["engine"] = TypedRef("engine", name.lower())
            elif full_prefix in spec.optional_params:
                # Explicit param names always win over OBJECT_TYPES matching
                params[full_prefix] = name
            elif type_prefix in OBJECT_TYPES or is_entity_type(type_prefix):
                targets.append(TypedRef(type_prefix, _slugify(name), namespace))
            else:
                # Unknown prefix stored as generic param (use full dotted key)
                params[full_prefix] = name

        elif kind == "PARAM_EQ":
            # key=value style param (alternative to key:value)
            consume()
            eq = val.index("=")
            key = val[:eq].lower()
            value = val[eq + 1:]
            if (value.startswith('"') and value.endswith('"')) or \
               (value.startswith("'") and value.endswith("'")):
                value = value[1:-1]
            params[key] = value

        elif kind == "RANGE":
            consume()
            params.setdefault("range", _parse_range(val, raw))

        elif kind == "WORD":
            consume()
            raise HSLSyntaxError(
                f"Unexpected bare word {val!r} — use typed references "
                f"(e.g. invariant:{val})",
                raw=raw, position=pos,
            )

        elif kind == "NUMBER":
            consume()
            raise HSLSyntaxError(
                f"Unexpected number {val!r} — use range:low..high", raw=raw
            )

        else:
            consume()
            raise HSLSyntaxError(f"Unexpected token {val!r}", raw=raw)

    return HSLCommand(
        verb=verb,
        subcommand=subcommand,
        targets=targets,
        params=params,
        raw=raw,
    )
