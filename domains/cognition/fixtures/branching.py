"""
Cognition Domain — Branching Decision Fixture
domains/cognition/fixtures/branching.py

A toy system that models possibility-space narrowing under configurable
constraint schedules.

At each step, the fixture maintains a count of "available branches" (a proxy
for possibility-space breadth). The constraint schedule determines how that
count changes over time. Perturbation can restore branches temporarily,
simulating disruption of the narrowing process.

This fixture is:
- Deterministic given the same seed and config
- Designed for controlled DCP event generation
- Suitable for testing collapse detection and morphology classification

Fixture ID: "branching"
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, asdict
from typing import Optional

from domains.cognition.analysis.trajectory import (
    TrajectoryEvent, TrajectoryLog, make_run_id,
    EVENT_SCHEMA_VERSION, LOG_SCHEMA_VERSION,
)
from domains.cognition.analysis.probes import (
    estimate_possibility_breadth,
    estimate_constraint_proxy,
    estimate_tension,
    detect_collapse,
    estimate_post_collapse_narrowing,
    estimate_perturbation_response,
    compute_qualification_status,
)
from domains.cognition.analysis.morphology_classifier import (
    classify_morphology, morphology_summary,
)

FIXTURE_ID   = "branching"
FIXTURE_TYPE = "Branching Decision Fixture"


@dataclass
class BranchingConfig:
    """
    Configuration for a BranchingFixture run.

    All parameters affect the trajectory shape and resulting DCP event structure.
    """

    initial_branches: int = 8
    """Starting number of available branches (unconstrained breadth)."""

    constraint_schedule: str = "linear"
    """
    How branches are removed over time:
        'linear'      — steady per-step reduction
        'step'        — sharp drop at midpoint of the run
        'exponential' — exponential decay toward 1 branch
        'none'        — no constraint (null control fixture)
    """

    n_steps: int = 60
    """Total steps to simulate."""

    collapse_threshold: float = 0.20
    """
    Possibility_breadth floor for collapse detection.
    Provisional value: 0.20 (i.e., 20% of initial breadth).
    For 8 initial branches: minimum breadth = 1/8 = 0.125, which is < 0.20.
    For 4 initial branches: minimum breadth = 1/4 = 0.25, which is > 0.20 (no collapse).
    Adjust per fixture or via calibration against a null corpus.
    """

    perturbation_step: Optional[int] = None
    """
    Step at which to inject a perturbation (restore some branches).
    None = no perturbation.
    """

    perturbation_magnitude: float = 0.40
    """
    Fraction of initial_branches to restore at perturbation_step.
    E.g., 0.40 = restore 40% of initial_branches back.
    Only used if perturbation_step is set.
    """

    noise: float = 0.0
    """
    Gaussian noise added to branch count at each step (std, in branch units).
    Use 0.0 for deterministic runs.
    """

    seed: int = 42
    """Random seed for noise and any stochastic elements."""


def run(config: BranchingConfig) -> TrajectoryLog:
    """
    Run a BranchingFixture and return the full TrajectoryLog.

    The fixture simulates possibility-space narrowing under a configurable
    constraint schedule. A perturbation can be injected at a specified step.

    Args:
        config: BranchingConfig instance

    Returns:
        TrajectoryLog with all per-step events and run-level summary fields
    """
    rng = random.Random(config.seed)

    initial = float(config.initial_branches)
    events: list[TrajectoryEvent] = []
    breadth_series: list[float] = []

    for step in range(config.n_steps):

        # --- Compute raw branch count before perturbation ---
        raw = _schedule_branches(config, step)

        # --- Apply perturbation if scheduled ---
        perturb_active = (
            config.perturbation_step is not None
            and step == config.perturbation_step
        )
        if perturb_active:
            restore = config.perturbation_magnitude * initial
            raw = min(initial, raw + restore)

        # --- Apply noise ---
        if config.noise > 0.0:
            raw += rng.gauss(0, config.noise)

        current = max(1.0, min(initial, raw))

        # --- Compute proxies ---
        breadth   = estimate_possibility_breadth(current, initial)
        constraint = estimate_constraint_proxy(initial, current, initial)
        breadth_series.append(breadth)
        tension   = estimate_tension(breadth_series)

        state_summary = {
            "current_branches": round(current, 2),
            "initial_branches": int(initial),
            "schedule":         config.constraint_schedule,
        }

        events.append(TrajectoryEvent(
            step                  = step,
            possibility_breadth   = round(breadth, 4),
            constraint_proxy      = round(constraint, 4),
            tension_proxy         = round(tension, 4),
            state_summary         = state_summary,
            perturbation_active   = perturb_active,
            schema_version        = EVENT_SCHEMA_VERSION,
        ))

    # --- Post-run analysis ---
    collapse_step = detect_collapse(
        breadth_series,
        threshold   = config.collapse_threshold,
        min_magnitude = 0.20,
    )

    post_narrowing  = estimate_post_collapse_narrowing(breadth_series, collapse_step)
    perturb_resp    = estimate_perturbation_response(
        breadth_series, config.perturbation_step
    ) if config.perturbation_step is not None else None

    morphology = classify_morphology(
        breadth_series,
        collapse_step   = collapse_step,
        initial_breadth = 1.0,  # always starts fully open
    )

    # --- Mark collapse step in events ---
    if collapse_step is not None:
        e = events[collapse_step]
        e.collapse_flag     = True
        e.collapse_morphology = morphology.value
        e.post_collapse_narrowing = post_narrowing

    qualification = compute_qualification_status(
        has_possibility_proxy = True,
        has_constraint_proxy  = True,
        has_tension_proxy     = any(e.tension_proxy > 0 for e in events),
        has_collapse_proxy    = collapse_step is not None,
        has_post_collapse     = post_narrowing is not None,
    )

    return TrajectoryLog(
        fixture_id           = FIXTURE_ID,
        fixture_type         = FIXTURE_TYPE,
        run_id               = make_run_id(FIXTURE_ID, config.seed),
        seed                 = config.seed,
        config               = asdict(config),
        events               = events,
        collapse_step        = collapse_step,
        final_morphology     = morphology.value,
        perturbation_step    = config.perturbation_step,
        perturbation_response = round(perturb_resp, 4) if perturb_resp is not None else None,
        qualification_status = qualification,
        schema_version       = LOG_SCHEMA_VERSION,
    )


# ---------------------------------------------------------------------------
# Constraint schedule implementations
# ---------------------------------------------------------------------------

def _schedule_branches(config: BranchingConfig, step: int) -> float:
    """Compute raw branch count at a given step under the configured schedule."""
    s    = config.constraint_schedule
    n    = config.n_steps
    init = float(config.initial_branches)

    if s == "none":
        return init

    elif s == "linear":
        # Reduce from initial to 1 linearly over n_steps
        rate = (init - 1.0) / max(1, n - 1)
        return init - step * rate

    elif s == "step":
        # Full breadth until midpoint, then collapse to 1
        return 1.0 if step >= n // 2 else init

    elif s == "exponential":
        # Asymptotic decay: branches = max(1, initial * exp(-k * step))
        k = math.log(init) / max(1, n - 1)  # reaches 1 at final step
        return max(1.0, init * math.exp(-k * step))

    else:
        raise ValueError(f"Unknown constraint_schedule: '{s!r}'")
