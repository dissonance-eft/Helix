"""
Test: Topological persistence — Class D / TOPOLOGICAL (kernel-002)

Prediction P1: For Class D systems, a single perturbation event of amplitude
δ < E_defect CANNOT change the topological invariant Q. The failure rate is
exactly zero below threshold, not merely small (contrast Class A: Kramers rate
is always finite for any δ > 0).

Model: 1D XY model on a periodic ring with N spins.
  θ_i ∈ [0, 2π): spin angle at site i
  Q=1 initial state: θ_i = 2πi/N (uniform winding)
  Bond difference: d_i = (θ_{i+1} - θ_i) wrapped to (-π, π] = 2π/N for Q=1 state
  Winding number: Q = round(Σ d_i / (2π))

How Q can change (defect insertion):
  A bond d_i wraps around ±π when the perturbed difference leaves (-π, π].
  If we kick all N spins independently by ε_i ∈ [-δ, δ], then bond i becomes:
    d_i = 2π/N + (ε_{i+1} - ε_i),  with ε_{i+1} - ε_i ∈ [-2δ, 2δ]
  A Q-change requires at least one bond to wrap: 2π/N + (ε_{i+1} - ε_i) > π
  Threshold: 2δ > π - 2π/N  →  δ > δ_c = π/2 - π/N

For N=20: δ_c = π/2 - π/20 ≈ 1.414 rad
  Sub-threshold: δ = 1.0 rad  → zero failure rate
  Super-threshold: δ = 2.0 rad → nonzero failure rate

Key: these tests apply ONE perturbation event per trial (not sequential drift).
     Topological protection is a PER-EVENT property, not a long-time stability
     under unconstrained random walk (which would require exchange coupling).
"""

import math
import random


def winding_number(thetas):
    """Compute integer winding number of spin configuration on a periodic ring."""
    total = 0.0
    N = len(thetas)
    for i in range(N):
        diff = thetas[(i + 1) % N] - thetas[i]
        diff = (diff + math.pi) % (2 * math.pi) - math.pi  # wrap to (-π, π]
        total += diff
    return round(total / (2 * math.pi))


def q1_state(N):
    """Q=1 state: uniform winding, θ_i = 2πi/N."""
    return [2 * math.pi * i / N for i in range(N)]


def single_event_perturbation(thetas, delta):
    """Apply ONE perturbation event: each spin kicked independently by ∈ [-δ, δ]."""
    return [theta + random.uniform(-delta, delta) for theta in thetas]


def failure_rate(N, delta, n_trials, seed):
    """
    Fraction of single-perturbation events (out of n_trials) that change Q.
    Each trial: fresh Q=1 state → one perturbation → check Q.
    """
    random.seed(seed)
    changes = 0
    Q_initial = winding_number(q1_state(N))
    for _ in range(n_trials):
        thetas = q1_state(N)
        thetas_perturbed = single_event_perturbation(thetas, delta)
        if winding_number(thetas_perturbed) != Q_initial:
            changes += 1
    return changes / n_trials


# ---------------------------------------------------------------------------
# Test 1: sub-threshold single events — zero failure rate (P1 core)
# ---------------------------------------------------------------------------

def test_below_threshold_zero_failure_rate(N=20, n_trials=2000, seed=42):
    """
    P1: For δ < δ_c, no single perturbation event can change Q.
    δ_c(N=20) = π/2 - π/20 ≈ 1.414 rad
    Test at δ_sub = 1.0 rad (0.71 × δ_c).
    """
    delta_c = math.pi / 2 - math.pi / N   # exact single-event threshold
    delta_sub = 1.0                         # well below δ_c ≈ 1.414

    assert delta_sub < delta_c, (
        f"Setup error: δ_sub={delta_sub:.3f} must be < δ_c={delta_c:.3f}"
    )

    rate = failure_rate(N, delta_sub, n_trials, seed)

    assert rate == 0.0, (
        f"FAIL P1: failure rate={rate:.4f} at δ={delta_sub:.3f} rad < δ_c={delta_c:.3f} rad. "
        "Class D predicts EXACTLY zero failure rate for single events below E_defect."
    )
    print(
        f"PASS P1: failure_rate=0.000 at δ_sub={delta_sub:.3f} rad "
        f"(δ_c={delta_c:.3f} rad, N={N}, {n_trials} trials)"
    )


# ---------------------------------------------------------------------------
# Test 2: super-threshold single events — nonzero failure rate
# ---------------------------------------------------------------------------

def test_above_threshold_nonzero_failure_rate(N=20, n_trials=1000, seed=42):
    """
    P1 complement: For δ > δ_c, some single events can change Q.
    Test at δ_super = 2.0 rad (1.41 × δ_c ≈ 1.414).
    """
    delta_c = math.pi / 2 - math.pi / N
    delta_super = 2.0  # above δ_c

    assert delta_super > delta_c, (
        f"Setup error: δ_super={delta_super:.3f} must be > δ_c={delta_c:.3f}"
    )

    rate = failure_rate(N, delta_super, n_trials, seed)

    assert rate > 0.0, (
        f"FAIL: failure rate=0 at δ={delta_super:.3f} rad > δ_c={delta_c:.3f} rad. "
        "Super-threshold events must be able to change Q."
    )
    print(
        f"PASS: failure_rate={rate:.4f} at δ_super={delta_super:.3f} rad "
        f"(δ_c={delta_c:.3f} rad, N={N}) — topological defect insertion confirmed"
    )


# ---------------------------------------------------------------------------
# Test 3: P1 contrast with Class A (Kramers) — discrete threshold structure
# ---------------------------------------------------------------------------

def test_threshold_is_sharp_not_arrhenius(N=20, n_trials=2000, seed=7):
    """
    P1 key distinction from Class A (BARRIER):
      Class A: failure rate ~ exp(-E_a/δ) — NONZERO for any δ > 0, always.
      Class D: failure rate = 0 for δ < δ_c, then nonzero above — DISCRETE threshold.

    We measure failure rate at three levels:
      δ_1 = 0.5 × δ_c  — well below threshold
      δ_2 = 0.9 × δ_c  — just below threshold
      δ_3 = 1.1 × δ_c  — just above threshold

    Prediction: rate(δ_1) = rate(δ_2) = 0.0 (exact).  rate(δ_3) > 0.
    A Class A system would give rate(δ_1) > 0 (very small but finite).
    """
    delta_c = math.pi / 2 - math.pi / N
    deltas = [0.5 * delta_c, 0.9 * delta_c, 1.1 * delta_c]
    rates = [failure_rate(N, d, n_trials, seed) for d in deltas]

    print(f"  Failure rates near threshold (δ_c={delta_c:.3f} rad, N={N}):")
    for d, r in zip(deltas, rates):
        label = "sub" if d < delta_c else "super"
        print(f"    δ={d:.4f} rad ({d/delta_c:.2f}×δ_c) [{label:5s}]: rate={r:.5f}")

    assert rates[0] == 0.0, (
        f"FAIL: rate(0.5×δ_c)={rates[0]:.5f} must be 0 for Class D below threshold"
    )
    assert rates[1] == 0.0, (
        f"FAIL: rate(0.9×δ_c)={rates[1]:.5f} must be 0 for Class D below threshold"
    )
    assert rates[2] > 0.0, (
        f"FAIL: rate(1.1×δ_c)={rates[2]:.5f} must be > 0 for Class D above threshold"
    )

    print(
        "  PASS: Discrete threshold confirmed — failure rate = 0 below δ_c, "
        f"nonzero above. (Class A would give nonzero rates at all δ > 0.)"
    )


# ---------------------------------------------------------------------------
# Test 4: threshold scales with N (Q is a topological, not geometric, property)
# ---------------------------------------------------------------------------

def test_threshold_scales_with_N(seed=13):
    """
    The defect creation threshold δ_c = π/2 - π/N increases with N.
    This confirms the topological character: harder to change Q in a larger ring
    (more bonds must cooperate to change the winding number in a single event).
    """
    print("  Threshold scaling with ring size N:")
    for N in [6, 10, 20, 40]:
        delta_c = math.pi / 2 - math.pi / N
        # Verify: δ just below threshold → zero failure rate
        rate_sub = failure_rate(N, delta_c * 0.9, n_trials=500, seed=seed)
        # Verify: δ just above threshold → nonzero failure rate
        rate_sup = failure_rate(N, delta_c * 1.1, n_trials=500, seed=seed)
        status = "PASS" if (rate_sub == 0.0 and rate_sup > 0.0) else "FAIL"
        print(
            f"    N={N:3d}: δ_c={delta_c:.4f} rad | "
            f"rate(0.9×δ_c)={rate_sub:.3f} | rate(1.1×δ_c)={rate_sup:.4f} | {status}"
        )
        assert rate_sub == 0.0, f"N={N}: rate below threshold must be 0"
        assert rate_sup > 0.0, f"N={N}: rate above threshold must be > 0"
    print("  PASS: Threshold scales correctly with N.")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== Test: Topological Persistence (Class D / kernel-002 P1) ===")
    print("Model: 1D XY ring; Q=1 winding number; single-event perturbation.\n")

    test_below_threshold_zero_failure_rate()
    test_above_threshold_nonzero_failure_rate()
    test_threshold_is_sharp_not_arrhenius()
    test_threshold_scales_with_N()

    print("\nAll topological persistence tests passed.")
