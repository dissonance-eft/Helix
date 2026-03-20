"""Tests for core.hsl.validator"""
"""Tests for core.hsl.validator"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import pytest
from core.hsl.parser import parse
from core.hsl.ast_nodes import HSLCommand, TypedRef
from core.hsl.validator import validate, validate_command
from core.hsl.errors import HSLValidationError, HSLUnknownTargetError


class TestValidate:
    def test_probe_valid(self):
        cmd = parse("PROBE invariant:decision_compression")
        result = validate(cmd)
        assert result is cmd  # returns same object

    def test_run_valid(self):
        cmd = parse("RUN experiment:decision_compression_probe engine:python")
        result = validate(cmd)
        assert result.verb == "RUN"

    def test_sweep_valid(self):
        cmd = parse("SWEEP parameter:coupling_strength range:0..1")
        result = validate(cmd)
        assert result.verb == "SWEEP"

    def test_compile_atlas_valid(self):
        cmd = parse("COMPILE atlas")
        result = validate(cmd)
        assert result.subcommand == "atlas"

    def test_integrity_check_valid(self):
        cmd = parse("INTEGRITY check")
        result = validate(cmd)
        assert result.subcommand == "check"

    def test_invalid_engine(self):
        cmd = parse("RUN experiment:decision_compression_probe engine:julia")
        with pytest.raises(HSLValidationError):
            validate(cmd)

    def test_atlas_registry_lookup_pass(self):
        registry = {
            "invariants": [{"id": "decision_compression"}],
        }
        cmd = parse("PROBE invariant:decision_compression")
        result = validate(cmd, registry=registry)
        assert result is cmd

    def test_atlas_registry_lookup_fail(self):
        registry = {
            "invariants": [{"id": "decision_compression"}],
        }
        cmd = parse("PROBE invariant:nonexistent_invariant")
        with pytest.raises(HSLUnknownTargetError):
            validate(cmd, registry=registry)


class TestValidateCommandCompat:
    """Compat API: validate_command(dict) -> {valid, error}"""

    def test_valid_dict(self):
        from core.hsl.normalizer import normalize_command
        d = normalize_command("PROBE invariant:decision_compression")
        result = validate_command(d)
        assert result["valid"] is True
        assert result["error"] is None

    def test_invalid_returns_false(self):
        result = validate_command({"verb": "unknown", "target": "x",
                                   "canonical": "INVALID something"})
        assert result["valid"] is False
        assert result["error"] is not None

    def test_empty_returns_false(self):
        result = validate_command({"verb": "", "target": "", "canonical": ""})
        assert result["valid"] is False
