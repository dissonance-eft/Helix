"""
Smoke test: Verify that KB objects carry the expected kernel-002 classification
fields (stability_class, persistence_type, mechanism_formalism) and that all
status values are correct.

This test does NOT run the dynamical simulations (P1, P2 tests do that).
It validates the STRUCTURAL properties of the KB objects only.

Runs from the Helix repo root: python tests/test_classifier_smoke.py
"""

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).parent.parent
KB = ROOT / "kb"

VALID_STABILITY_CLASSES = {
    "BARRIER", "THROUGHPUT", "CRITICAL", "TOPOLOGICAL",
    "NOISE_CONSTRUCTIVE", "HYBRID", "UNCLASSIFIED"
}

VALID_PERSISTENCE_TYPES = {"STATE", "PATTERN"}

VALID_MECHANISM_FORMALISMS = {"TST", "ISS", "RG", "TOPO", "NOISE", "OTHER"}

VALID_STATUSES = {"CAPTURE", "STRESS_TESTED", "COMPRESSED", "DEPRECATED"}

# Expected classification for claims that carry kernel-002 fields
EXPECTED_CLASSIFICATIONS = {
    "ont-001": {"stability_class": "THROUGHPUT", "persistence_type": "STATE"},
    "ont-002": {"stability_class": "HYBRID",     "persistence_type": "STATE"},
    "ont-003": {"stability_class": "THROUGHPUT", "persistence_type": "STATE"},
    "ont-004": {"stability_class": "CRITICAL",   "persistence_type": "STATE"},
}

EXPECTED_STATUSES = {
    "kernel-000": "DEPRECATED",
    "kernel-001": "DEPRECATED",
    "kernel-002": "CAPTURE",
    "ont-001":    "STRESS_TESTED",
    "ont-002":    "STRESS_TESTED",
    "ont-003":    "STRESS_TESTED",
    "ont-004":    "STRESS_TESTED",
    "ont-005":    "DEPRECATED",
}

# Required schema fields for all KB objects
REQUIRED_FIELDS = ["id", "type", "statement", "assumptions", "falsifiers", "status", "references"]


def load_kb():
    objects = {}
    for f in sorted(KB.glob("*.json")):
        try:
            with f.open(encoding="utf-8") as fh:
                objects[f.stem] = json.load(fh)
        except Exception as e:
            print(f"ERROR loading {f.name}: {e}")
            sys.exit(1)
    return objects


# ---------------------------------------------------------------------------
# Individual test functions — each returns True on pass, raises on fail
# ---------------------------------------------------------------------------

def test_kb_directory_exists():
    assert KB.exists(), f"kb/ directory not found at {KB}"
    print("PASS: kb/ directory exists")


def test_all_objects_parseable(objects):
    assert len(objects) > 0, "kb/ is empty — nothing to test"
    print(f"PASS: {len(objects)} KB objects loaded successfully")


def test_required_schema_fields(objects):
    """All objects must have the 7 required schema fields."""
    failures = []
    for obj_id, obj in objects.items():
        for field in REQUIRED_FIELDS:
            if field not in obj:
                failures.append(f"  {obj_id}: missing required field '{field}'")
    if failures:
        raise AssertionError("Missing required fields:\n" + "\n".join(failures))
    print(f"PASS: All {len(objects)} objects have required schema fields")


def test_kernel_002_exists(objects):
    assert "kernel-002" in objects, "kernel-002.json missing from kb/"
    k = objects["kernel-002"]
    assert k.get("status") == "CAPTURE", (
        f"kernel-002 expected status=CAPTURE, got {k.get('status')}"
    )
    print("PASS: kernel-002.json present with status=CAPTURE")


def test_status_values(objects):
    """Verify status values match expected for all tracked objects."""
    failures = []
    for obj_id, expected_status in EXPECTED_STATUSES.items():
        if obj_id not in objects:
            failures.append(f"  {obj_id}: missing from kb/")
            continue
        actual = objects[obj_id].get("status")
        if actual not in VALID_STATUSES:
            failures.append(f"  {obj_id}: invalid status '{actual}'")
        elif actual != expected_status:
            failures.append(
                f"  {obj_id}: expected status={expected_status}, got {actual}"
            )
    if failures:
        raise AssertionError("Status mismatches:\n" + "\n".join(failures))
    print(f"PASS: All {len(EXPECTED_STATUSES)} tracked objects have correct status")


def test_stability_class_values(objects):
    """ont-001..004 must have valid, expected stability_class values."""
    failures = []
    for obj_id, expected in EXPECTED_CLASSIFICATIONS.items():
        if obj_id not in objects:
            failures.append(f"  {obj_id}: missing from kb/")
            continue
        obj = objects[obj_id]
        sc = obj.get("stability_class")
        if sc is None:
            failures.append(f"  {obj_id}: missing stability_class")
        elif sc not in VALID_STABILITY_CLASSES:
            failures.append(f"  {obj_id}: stability_class '{sc}' not in valid set")
        elif sc != expected["stability_class"]:
            failures.append(
                f"  {obj_id}: expected stability_class={expected['stability_class']}, got {sc}"
            )
    if failures:
        raise AssertionError("stability_class failures:\n" + "\n".join(failures))
    print("PASS: All stability_class values are valid and match expected classifications")


def test_persistence_type_values(objects):
    """ont-001..004 must have valid, expected persistence_type values."""
    failures = []
    for obj_id, expected in EXPECTED_CLASSIFICATIONS.items():
        if obj_id not in objects:
            continue
        obj = objects[obj_id]
        pt = obj.get("persistence_type")
        if pt is None:
            failures.append(f"  {obj_id}: missing persistence_type")
        elif pt not in VALID_PERSISTENCE_TYPES:
            failures.append(f"  {obj_id}: persistence_type '{pt}' not in {VALID_PERSISTENCE_TYPES}")
        elif pt != expected["persistence_type"]:
            failures.append(
                f"  {obj_id}: expected persistence_type={expected['persistence_type']}, got {pt}"
            )
    if failures:
        raise AssertionError("persistence_type failures:\n" + "\n".join(failures))
    print("PASS: All persistence_type values are valid and match expected")


def test_mechanism_formalism_values(objects):
    """ont-001..004 must have a valid mechanism_formalism field."""
    failures = []
    for obj_id in EXPECTED_CLASSIFICATIONS:
        if obj_id not in objects:
            continue
        obj = objects[obj_id]
        mf = obj.get("mechanism_formalism")
        if mf is None:
            failures.append(f"  {obj_id}: missing mechanism_formalism")
        elif mf not in VALID_MECHANISM_FORMALISMS:
            failures.append(
                f"  {obj_id}: mechanism_formalism '{mf}' not in {VALID_MECHANISM_FORMALISMS}"
            )
    if failures:
        raise AssertionError("mechanism_formalism failures:\n" + "\n".join(failures))
    print("PASS: All mechanism_formalism values are valid")


def test_deprecated_have_decay_chain(objects):
    """DEPRECATED objects must have a non-empty decay_chain."""
    failures = []
    for obj_id, obj in objects.items():
        if obj.get("status") == "DEPRECATED":
            dc = obj.get("decay_chain", [])
            if not isinstance(dc, list) or len(dc) == 0:
                failures.append(f"  {obj_id}: DEPRECATED but has no decay_chain")
    if failures:
        raise AssertionError("Missing decay_chain on DEPRECATED objects:\n" + "\n".join(failures))
    print("PASS: All DEPRECATED objects have non-empty decay_chain")


def test_kernel_002_has_predictions(objects):
    """kernel-002 must carry predictions field with P1 and P2 entries."""
    k = objects.get("kernel-002", {})
    preds = k.get("predictions", [])
    assert isinstance(preds, list), "kernel-002 predictions field must be a list"
    assert len(preds) >= 2, (
        f"kernel-002 must have at least 2 predictions (P1, P2), found {len(preds)}"
    )
    pred_str = " ".join(preds)
    assert "P1" in pred_str, "kernel-002 predictions must include P1 (TOPOLOGICAL)"
    assert "P2" in pred_str, "kernel-002 predictions must include P2 (NOISE_CONSTRUCTIVE)"
    print(f"PASS: kernel-002 has {len(preds)} prediction(s) including P1 and P2")


def test_ont_004_has_de_break_tests(objects):
    """ont-004 must have break_tests that target Class D and Class E."""
    obj = objects.get("ont-004", {})
    bts = obj.get("break_tests", [])
    texts = " ".join(
        bt.get("setup", "") + bt.get("verdict", "")
        for bt in bts
        if isinstance(bt, dict)
    )
    assert "Class D" in texts, "ont-004 must have a Class D break test"
    assert "Class E" in texts, "ont-004 must have a Class E break test"
    print("PASS: ont-004 has Class D and Class E break tests")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Helix KB Classifier Smoke Tests (kernel-002) ===\n")

    test_kb_directory_exists()
    objects = load_kb()
    test_all_objects_parseable(objects)

    test_functions = [
        test_required_schema_fields,
        test_kernel_002_exists,
        test_status_values,
        test_stability_class_values,
        test_persistence_type_values,
        test_mechanism_formalism_values,
        test_deprecated_have_decay_chain,
        test_kernel_002_has_predictions,
        test_ont_004_has_de_break_tests,
    ]

    failures = []
    for fn in test_functions:
        try:
            fn(objects)
        except AssertionError as e:
            print(f"FAIL: {e}")
            failures.append(str(e))

    print(f"\n{'=' * 50}")
    if failures:
        print(f"FAILED: {len(failures)} test(s) failed.")
        sys.exit(1)
    else:
        print(f"ALL PASSED: {len(test_functions)} smoke tests passed.")
        sys.exit(0)
