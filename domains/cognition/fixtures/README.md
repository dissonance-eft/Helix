# Cognition Domain — Fixtures

**Status**: Defined, not implemented  
**Updated**: 2026-03-21

This directory will hold canonical fixture classes for the cognition domain once
implementation begins. It exists to name and specify intended fixtures forward.

---

## First Intended Fixture: Toy Branching Agent

**Name**: `toy_branching_agent`  
**File**: `toy_branching_agent.py` (not yet written)

### Purpose

A toy agent that traverses a decision tree with a tunable branching factor and
constraint schedule. This provides:

- Controlled manipulation of `possibility_breadth` (set by branching factor)
- Scheduled collapse events at known trajectory points with ground-truth morphology
- Perturbation injection at defined trajectory positions
- Repeatable, deterministic runs for validation harness use

### Fixture Sections (target, matching math/validation pattern)

| Section | Description | Status |
|---------|-------------|--------|
| A — Metric sanity | Verify `possibility_breadth` behaves monotonically under forced constraint schedule | Not implemented |
| B — Scheduled collapse | Produce a collapse event at a known step with known morphology label | Not implemented |
| C — Perturbation recovery | Inject disruption mid-trajectory; measure `perturbation_response` shape | Not implemented |
| D — Morphology discrimination | Confirm classifier correctly labels TRANSFORMATIVE vs CIRCULAR under distinct schedules | Not implemented |

### Parameters (target)

```python
ToyBranchingAgentConfig(
    branching_factor_initial = 8,      # initial possibility_breadth
    constraint_schedule = "linear",    # how breadth narrows
    collapse_step = 40,                # when to force a sharp transition
    collapse_type = "TRANSFORMATIVE",  # ground-truth morphology
    perturbation_step = None,          # optional: inject at this step
    perturbation_magnitude = 0.0,
    seed = 42,
)
```

### Output (target)

Produces a `CognitionStateArtifact` (see `SPEC.md §5`) with known ground-truth
labels, suitable for validating the collapse detection and morphology classification
pipeline stages.

---

## Second Intended Fixture: AI Decision Probe

**Name**: `ai_decision_probe` (placeholder name)  
**Status**: Named only — not specified

Intended to apply the cognition pipeline to an AI system's token probability
distribution across a constrained generation task, treating token entropy as a
proxy for `possibility_breadth`.

Specification deferred until Stage 2 (state-space estimation) is implemented.
