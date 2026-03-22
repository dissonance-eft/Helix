"""
Cognition Domain — Attractor Basin Fixture
domains/cognition/fixtures/attractor.py

A toy system that models state dynamics in a discretized possibility space
with an attractor region and perturbable initial conditions.

The fixture maintains a probability distribution over N discrete states.
At each step, the distribution is pulled toward an attractor basin by a
tunable attractor_strength parameter. Possibility breadth is computed from
the effective entropy of the distribution relative to maximum entropy.

This fixture is particularly useful for studying:
- Circular collapse: system drifts toward attractor then returns
- Transformative collapse: system locks into a new, narrow high-probability region
- Deferred / suspended collapse: system hovers near the attractor boundary
- Perturbation recovery: knocking the distribution and observing re-attraction

Fixture ID: "attractor"
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

FIXTURE_ID   = "attractor"
FIXTURE_TYPE = "Attractor Basin Fixture"


@dataclass
class AttractorConfig:
    """
    Configuration for an AttractorFixture run.
    """

    n_states: int = 16
    """
    Number of discrete states in the possibility space.
    Possibility-space breadth is measured as effective entropy / max entropy.
    """

    attractor_size: int = 4
    """
    Number of states that form the attractor basin.
    These states receive extra probability mass at each step.
    Must be < n_states.
    """

    attractor_strength: float = 0.05
    """
    Per-step mixing coefficient toward the attractor basin.
    Higher = faster convergence to attractor.
    Range: [0.0, 1.0]. 0.0 = no attraction; 1.0 = instant lock.
    """

    n_steps: int = 80
    """Total steps to simulate."""

    collapse_threshold: float = 0.35
    """
    Possibility_breadth floor for collapse detection (entropy-based breadth).
    Provisional value: 0.35. A 16-state system pulled to a 4-state attractor
    reaches ~0.25 effective breadth — below this threshold.
    Adjust per fixture or via calibration against a null corpus.
    """

    perturbation_step: Optional[int] = None
    """
    Step at which to inject a perturbation.
    Perturbation disperses the probability distribution toward uniform
    (expanding possibility space temporarily).
    """

    perturbation_magnitude: float = 0.50
    """
    Fraction of uniform distribution to mix in at perturbation step.
    0.0 = no change; 1.0 = full reset to uniform.
    """

    seed: int = 42
    """Random seed for initialization."""


def run(config: AttractorConfig) -> TrajectoryLog:
    """
    Run an AttractorFixture and return the full TrajectoryLog.

    The fixture maintains a probability distribution P over n_states discrete
    states. At each step, P is updated by mixing in the attractor basin
    distribution with weight attractor_strength.

    Possibility breadth is the effective number of states (exp(H)) normalized
    by total n_states, where H is the Shannon entropy of P.

    Args:
        config: AttractorConfig instance

    Returns:
        TrajectoryLog with all per-step events and run-level summary fields
    """
    rng = random.Random(config.seed)

    n       = config.n_states
    asize   = min(config.attractor_size, n - 1)
    alpha   = config.attractor_strength

    # Initial distribution: uniform over all states
    dist = [1.0 / n] * n

    # Attractor basin distribution: uniform over first asize states
    attractor_dist = [1.0 / asize if i < asize else 0.0 for i in range(n)]

    events: list[TrajectoryEvent] = []
    breadth_series: list[float] = []
    initial_breadth_set = False
    initial_breadth = 1.0

    for step in range(config.n_steps):

        # --- Apply attractor pull ---
        dist = [
            (1.0 - alpha) * dist[i] + alpha * attractor_dist[i]
            for i in range(n)
        ]

        # --- Apply perturbation if scheduled ---
        perturb_active = (
            config.perturbation_step is not None
            and step == config.perturbation_step
        )
        if perturb_active:
            beta = config.perturbation_magnitude
            uniform = [1.0 / n] * n
            dist = [(1.0 - beta) * dist[i] + beta * uniform[i] for i in range(n)]

        # Normalize (floating point safety)
        total = sum(dist)
        dist  = [p / total for p in dist]

        # --- Compute breadth from entropy ---
        breadth = _entropy_breadth(dist, n)
        if not initial_breadth_set:
            initial_breadth = breadth
            initial_breadth_set = True

        constraint = estimate_constraint_proxy(initial_breadth, breadth, initial_breadth)
        breadth_series.append(breadth)
        tension = estimate_tension(breadth_series)

        # Dominant state (for state summary)
        dominant_state = max(range(n), key=lambda i: dist[i])
        in_attractor   = dominant_state < asize

        state_summary = {
            "dominant_state":    dominant_state,
            "in_attractor":      in_attractor,
            "attractor_prob":    round(sum(dist[:asize]), 4),
            "effective_n_states": round(math.exp(_raw_entropy(dist)), 2),
        }

        events.append(TrajectoryEvent(
            step                = step,
            possibility_breadth = round(breadth, 4),
            constraint_proxy    = round(constraint, 4),
            tension_proxy       = round(tension, 4),
            state_summary       = state_summary,
            perturbation_active = perturb_active,
            schema_version      = EVENT_SCHEMA_VERSION,
        ))

    # --- Post-run analysis ---
    collapse_step = detect_collapse(
        breadth_series,
        threshold     = config.collapse_threshold,
        min_magnitude = 0.20,
    )

    post_narrowing = estimate_post_collapse_narrowing(breadth_series, collapse_step)
    perturb_resp   = estimate_perturbation_response(
        breadth_series, config.perturbation_step
    ) if config.perturbation_step is not None else None

    morphology = classify_morphology(
        breadth_series,
        collapse_step   = collapse_step,
        initial_breadth = initial_breadth,
    )

    if collapse_step is not None:
        e = events[collapse_step]
        e.collapse_flag           = True
        e.collapse_morphology     = morphology.value
        e.post_collapse_narrowing = post_narrowing

    qualification = compute_qualification_status(
        has_possibility_proxy = True,
        has_constraint_proxy  = True,
        has_tension_proxy     = any(e.tension_proxy > 0 for e in events),
        has_collapse_proxy    = collapse_step is not None,
        has_post_collapse     = post_narrowing is not None,
    )

    return TrajectoryLog(
        fixture_id            = FIXTURE_ID,
        fixture_type          = FIXTURE_TYPE,
        run_id                = make_run_id(FIXTURE_ID, config.seed),
        seed                  = config.seed,
        config                = asdict(config),
        events                = events,
        collapse_step         = collapse_step,
        final_morphology      = morphology.value,
        perturbation_step     = config.perturbation_step,
        perturbation_response = round(perturb_resp, 4) if perturb_resp is not None else None,
        qualification_status  = qualification,
        schema_version        = LOG_SCHEMA_VERSION,
    )


# ---------------------------------------------------------------------------
# Entropy utilities
# ---------------------------------------------------------------------------

def _raw_entropy(dist: list[float]) -> float:
    """Shannon entropy H of a distribution (nats)."""
    h = 0.0
    for p in dist:
        if p > 1e-12:
            h -= p * math.log(p)
    return h


def _entropy_breadth(dist: list[float], n: int) -> float:
    """
    Possibility breadth as effective state fraction from entropy.
    breadth = exp(H) / n   where H is Shannon entropy in nats.
    Range: [1/n, 1.0]
    """
    h = _raw_entropy(dist)
    return min(1.0, math.exp(h) / n)
