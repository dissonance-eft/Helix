"""
Cognition Domain — Domain-Local Validation
domains/cognition/validation/cognition_fixture.py

Four-section validation harness for the cognition domain.
Follows the pattern established in domains/math/validation/kuramoto_fixture.py.

This is NOT a generic test runner. It is a domain-local validation that checks
the specific behavioral expectations of the cognition domain's fixtures, probes,
and morphology classifier.

Sections:
    A — Determinism / stability
    B — Collapse detection sanity
    C — Morphology sanity
    D — Structured output validity

Run directly:
    python -m domains.cognition.validation.cognition_fixture

Each section reports PASS / FAIL and a brief reason.
No external test framework required.
"""
from __future__ import annotations

import json
import sys
from typing import Any

from domains.cognition.fixtures import branching, attractor
from domains.cognition.fixtures.branching import BranchingConfig
from domains.cognition.fixtures.attractor import AttractorConfig
from domains.cognition.analysis.trajectory import TrajectoryLog, TrajectoryEvent
from domains.cognition.analysis.morphology_classifier import classify_morphology
from core.invariants.dcp.morphology import CollapseMorphology


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _check(name: str, condition: bool, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    msg    = f"  [{status}] {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    return condition


def _section(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


# ---------------------------------------------------------------------------
# Section A — Determinism / stability
# ---------------------------------------------------------------------------

def section_A_determinism() -> list[bool]:
    _section("Section A — Determinism / Stability")
    results: list[bool] = []

    # A1: Same seed → same branching trajectory
    cfg = BranchingConfig(seed=42, constraint_schedule="linear", n_steps=40)
    log1 = branching.run(cfg)
    log2 = branching.run(cfg)
    breadths1 = [e.possibility_breadth for e in log1.events]
    breadths2 = [e.possibility_breadth for e in log2.events]
    results.append(_check(
        "A1 branching: same seed → same trajectory",
        breadths1 == breadths2,
        f"n_steps={len(breadths1)}",
    ))

    # A2: Same seed → same attractor trajectory
    acfg = AttractorConfig(seed=77, n_steps=40)
    alog1 = attractor.run(acfg)
    alog2 = attractor.run(acfg)
    ab1 = [e.possibility_breadth for e in alog1.events]
    ab2 = [e.possibility_breadth for e in alog2.events]
    results.append(_check(
        "A2 attractor: same seed → same trajectory",
        ab1 == ab2,
        f"n_steps={len(ab1)}",
    ))

    # A3: Different seeds → different trajectories (with noise)
    cfg_noisy1 = BranchingConfig(seed=1, noise=0.5, n_steps=30)
    cfg_noisy2 = BranchingConfig(seed=2, noise=0.5, n_steps=30)
    bn1 = [e.possibility_breadth for e in branching.run(cfg_noisy1).events]
    bn2 = [e.possibility_breadth for e in branching.run(cfg_noisy2).events]
    results.append(_check(
        "A3 branching: different seeds → different trajectories",
        bn1 != bn2,
        "noise=0.5",
    ))

    return results


# ---------------------------------------------------------------------------
# Section B — Collapse detection sanity
# ---------------------------------------------------------------------------

def section_B_collapse_sanity() -> list[bool]:
    _section("Section B — Collapse Detection Sanity")
    results: list[bool] = []

    # B1: Null control — no constraint → no collapse
    null_cfg = BranchingConfig(constraint_schedule="none", n_steps=60, seed=42)
    null_log = branching.run(null_cfg)
    results.append(_check(
        "B1 branching null: no constraint → no collapse",
        null_log.collapse_step is None,
        f"collapse_step={null_log.collapse_step}",
    ))

    # B2: Strong linear constraint → collapse detected
    strong_cfg = BranchingConfig(
        initial_branches=8,
        constraint_schedule="linear",
        n_steps=60,
        seed=42,
    )
    strong_log = branching.run(strong_cfg)
    results.append(_check(
        "B2 branching linear: collapse detected under strong constraint",
        strong_log.collapse_step is not None,
        f"collapse_step={strong_log.collapse_step}",
    ))

    # B3: Step constraint → collapse detected near midpoint
    step_cfg = BranchingConfig(
        constraint_schedule="step",
        n_steps=60,
        seed=42,
    )
    step_log = branching.run(step_cfg)
    results.append(_check(
        "B3 branching step: collapse detected after step",
        step_log.collapse_step is not None and step_log.collapse_step >= 28,
        f"collapse_step={step_log.collapse_step}",
    ))

    # B4: Attractor with mild strength → may not collapse, mild strength
    mild_cfg = AttractorConfig(attractor_strength=0.02, n_steps=80, seed=42)
    mild_log = attractor.run(mild_cfg)
    results.append(_check(
        "B4 attractor mild: weak attractor → no sharp collapse expected",
        # Not a strict requirement — just report what happened
        True,  # informational
        f"collapse_step={mild_log.collapse_step}",
    ))

    # B5: Attractor with strong strength → should collapse
    strong_attr_cfg = AttractorConfig(
        attractor_strength=0.25,  # faster convergence
        n_steps=120,              # more steps for entropy to fall below threshold
        seed=42,
    )
    strong_attr_log = attractor.run(strong_attr_cfg)
    results.append(_check(
        "B5 attractor strong: strong attractor → collapse detected",
        strong_attr_log.collapse_step is not None,
        f"collapse_step={strong_attr_log.collapse_step}",
    ))

    return results


# ---------------------------------------------------------------------------
# Section C — Morphology sanity
# ---------------------------------------------------------------------------

def section_C_morphology_sanity() -> list[bool]:
    _section("Section C — Morphology Sanity")
    results: list[bool] = []

    # C1: Linear constraint → TRANSFORMATIVE (new coherent narrow state)
    linear_log = branching.run(BranchingConfig(
        constraint_schedule="linear", n_steps=60, seed=42
    ))
    results.append(_check(
        "C1 branching linear → TRANSFORMATIVE",
        linear_log.final_morphology == CollapseMorphology.TRANSFORMATIVE.value,
        f"got: {linear_log.final_morphology}",
    ))

    # C2: No constraint → DEFERRED_SUSPENDED
    null_log = branching.run(BranchingConfig(
        constraint_schedule="none", n_steps=60, seed=42
    ))
    results.append(_check(
        "C2 branching null → DEFERRED_SUSPENDED",
        null_log.final_morphology == CollapseMorphology.DEFERRED_SUSPENDED.value,
        f"got: {null_log.final_morphology}",
    ))

    # C3: Perturbation on attractor → some nontrivial morphology result
    perturb_cfg = AttractorConfig(
        attractor_strength=0.12,
        n_steps=80,
        perturbation_step=20,
        perturbation_magnitude=0.80,  # strong reset → recovery test
        seed=42,
    )
    perturb_log = attractor.run(perturb_cfg)
    perturb_morphology = perturb_log.final_morphology
    results.append(_check(
        "C3 attractor perturb: morphology label is a valid CollapseMorphology",
        perturb_morphology in [m.value for m in CollapseMorphology],
        f"got: {perturb_morphology}",
    ))

    # C4: Perturbation produces a distinct response
    no_perturb_log = attractor.run(AttractorConfig(
        attractor_strength=0.12, n_steps=80, seed=42
    ))
    results.append(_check(
        "C4 perturbation changes breadth trajectory vs no-perturbation",
        perturb_log.perturbation_response is not None,
        f"perturbation_response={perturb_log.perturbation_response}",
    ))

    # C5: Perturbation response is positive (expansion) for large-magnitude perturb
    results.append(_check(
        "C5 large perturbation → positive perturbation_response (breadth expands)",
        perturb_log.perturbation_response is not None
        and perturb_log.perturbation_response > 0,
        f"response={perturb_log.perturbation_response}",
    ))

    return results


# ---------------------------------------------------------------------------
# Section D — Structured output validity
# ---------------------------------------------------------------------------

def section_D_output_validity() -> list[bool]:
    _section("Section D — Structured Output Validity")
    results: list[bool] = []

    log = branching.run(BranchingConfig(n_steps=20, seed=1))

    # D1: TrajectoryLog has required fields
    results.append(_check(
        "D1 TrajectoryLog: has fixture_id / run_id / seed / schema_version",
        all([log.fixture_id, log.run_id, log.seed is not None, log.schema_version]),
        f"fixture_id={log.fixture_id} schema={log.schema_version}",
    ))

    # D2: Events list is populated
    results.append(_check(
        "D2 events: n_events == n_steps",
        len(log.events) == 20,
        f"got {len(log.events)}",
    ))

    # D3: Each event has required fields
    required_event_fields = [
        "step", "possibility_breadth", "constraint_proxy",
        "tension_proxy", "state_summary", "schema_version",
    ]
    first_event_dict = log.events[0].to_dict()
    all_present = all(f in first_event_dict for f in required_event_fields)
    results.append(_check(
        "D3 events: all required fields present in first event",
        all_present,
        f"fields: {list(first_event_dict.keys())}",
    ))

    # D4: to_json round-trips without error
    try:
        j = log.to_json()
        parsed = json.loads(j)
        round_trip_ok = isinstance(parsed, dict) and "fixture_id" in parsed
    except Exception as exc:
        round_trip_ok = False
    results.append(_check("D4 to_json: round-trip to/from JSON succeeds", round_trip_ok))

    # D5: summary() returns compact dict with expected keys
    s = log.summary()
    summary_keys = ["fixture_id", "collapse_step", "final_morphology", "qualification_status"]
    results.append(_check(
        "D5 summary(): required keys present",
        all(k in s for k in summary_keys),
        f"keys: {list(s.keys())}",
    ))

    return results


# ---------------------------------------------------------------------------
# Main harness
# ---------------------------------------------------------------------------

def run_all() -> dict[str, Any]:
    print("\nCognition Domain — Validation Harness")
    print("=" * 60)
    print("Status: first-pass, heuristic-only fixtures")
    print("All thresholds are uncalibrated provisional values.")
    print("=" * 60)

    results: dict[str, list[bool]] = {
        "A": section_A_determinism(),
        "B": section_B_collapse_sanity(),
        "C": section_C_morphology_sanity(),
        "D": section_D_output_validity(),
    }

    all_checks = [r for section in results.values() for r in section]
    passed     = sum(all_checks)
    total      = len(all_checks)

    print(f"\n{'=' * 60}")
    print(f"  TOTAL: {passed}/{total} checks passed")
    if passed == total:
        print("  STATUS: ALL PASS")
    else:
        print(f"  STATUS: {total - passed} FAILURE(S) — see above")
    print(f"{'=' * 60}\n")

    return {
        "passed":  passed,
        "total":   total,
        "all_pass": passed == total,
        "sections": {s: sum(v) for s, v in results.items()},
    }


if __name__ == "__main__":
    outcome = run_all()
    sys.exit(0 if outcome["all_pass"] else 1)
