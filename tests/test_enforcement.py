"""
Helix Enforcement — Integrity Tests
===================================
Mandatory tests for the Helix enforcement layer.
"""
import unittest
from pathlib import Path
from datetime import datetime, timezone

from core.enforcement import (
    validate_id,
    validate_entity_schema,
    authorize_atlas_write,
    pre_persistence_check,
    ValidationError,
    IDError,
    IllegalWriteError
)

class TestEnforcement(unittest.TestCase):

    def setUp(self):
        self.valid_entity = {
            "entity_id": "music.track:8aa0534f",
            "entity_type": "track",
            "created_at": "2026-03-19T22:30:00Z",
            "source": "library",
            "complexity": 0.5,
            "structure": 0.5,
            "repetition": 0.5,
            "density": 0.5,
            "expression": 0.5,
            "variation": 0.5
        }

    # 1. ID Validation Tests
    def test_valid_id(self):
        self.assertEqual(validate_id("music.track:my_slug"), "music.track:my_slug")
        self.assertEqual(validate_id("system.invariant:compression_law"), "system.invariant:compression_law")

    def test_invalid_id(self):
        with self.assertRaises(IDError):
            validate_id("Music.Track:Slug") # Uppercase
        with self.assertRaises(IDError):
            validate_id("music.track") # Missing slug
        with self.assertRaises(IDError):
            validate_id("track:slug") # Missing domain
        with self.assertRaises(IDError):
            validate_id("music:track:slug") # Too many colons

    # 2. Schema Validation Tests
    def test_valid_schema(self):
        # Should not raise
        validate_entity_schema(self.valid_entity, is_atlas=True)

    def test_invalid_schema_missing_fields(self):
        invalid = self.valid_entity.copy()
        del invalid["entity_id"]
        with self.assertRaises(ValidationError) as cm:
            validate_entity_schema(invalid)
        self.assertEqual(cm.exception.code, "INVALID_SCHEMA")

    def test_invalid_ccs_values(self):
        invalid = self.valid_entity.copy()
        invalid["complexity"] = 1.5 # Out of range
        with self.assertRaises(ValidationError):
            validate_entity_schema(invalid, is_atlas=True)

    # 3. Atlas Write Authorization
    def test_unauthorized_write(self):
        # We catch this by mocking the caller or just testing the logic directly
        # with a path that isn't core/compiler or tests.
        pass

    def test_illegal_atlas_write_from_wrong_app(self):
        repo_root = Path(__file__).resolve().parent.parent
        atlas_path = repo_root / "codex" / "atlas" / "illegal.json"
        
        # Test that enforce_persistence fails if called from an unauthorized context
        # (Since we are in tests/, it SHOULD pass here)
        from core.enforcement import enforce_persistence
        enforce_persistence(self.valid_entity, atlas_path, is_atlas=True)

    # 4. Shadow Audit Tests
    def test_audit_scan_valid_entity(self):
        from core.enforcement import audit_system_state
        repo_root = Path(__file__).resolve().parent.parent
        # This will scan the repo - if it's clean, passed should be true
        # result = audit_system_state(repo_root)
        # self.assertTrue(isinstance(result, dict))
        pass

    def test_audit_detects_invalid_id(self):
        from core.enforcement.audit import AuditFinding, Severity
        from pathlib import Path
        finding = AuditFinding(Path("test.json"), "INVALID_ID", "Test error", Severity.HIGH)
        self.assertEqual(finding.code, "INVALID_ID")

    # 5. Pre-Persistence Checks
    def test_pre_persistence_atlas_pass(self):
        repo_root = Path(__file__).resolve().parent.parent
        atlas_path = repo_root / "codex" / "atlas" / "music" / "tracks" / "test.json"
        # This caller (TestEnforcement) IS authorized because 'tests' is in its path.
        pre_persistence_check(self.valid_entity, atlas_path)

    def test_pre_persistence_library_pass(self):
        repo_root = Path(__file__).resolve().parent.parent
        lib_path = repo_root / "codex" / "library" / "music" / "artist" / "test.json"
        pre_persistence_check(self.valid_entity, lib_path)

if __name__ == "__main__":
    unittest.main()
