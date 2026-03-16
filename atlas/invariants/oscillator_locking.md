# Invariant: Oscillator Locking

**Type:** Invariant
**Status:** Verified
**Origin:** Helix cross-domain probe — games, language, music
**Confidence:** Verified (3/3 runs, mean signal 0.991)
**Last Updated:** 2026-03-15

---

## Domain Coverage

- Games (discrete competitive systems)
- Language (sequential symbolic systems)
- Music (temporal rhythmic structures)
- Spatial substrate: pending (Phase 9)

---

## Mechanism

Coupled oscillating subsystems synchronize into phase-locked states when
interaction strength crosses a critical coupling threshold. Once locked,
the system resists perturbation — phase coherence is maintained against
moderate noise. The transition to locking is sharp, suggesting a genuine
phase transition rather than smooth interpolation.

The near-unity signal (mean 0.991) across all tested substrates makes this
the strongest raw signal in the Helix Atlas.

---

## Predictions

1. Phase-locking signal > 0.95 in any substrate with genuine coupled oscillation
2. Sharp transition at a critical coupling threshold (not gradual onset)
3. Post-locking stability against low-amplitude noise
4. The music substrate's slightly lower signal (0.974) should replicate
   consistently — if it regresses toward 0.99, it was noise; if it stays
   lower, music has a structurally distinct coupling regime

---

## Falsifiers

1. Any coupled oscillating system showing signal < 0.90 under standard conditions
2. Gradual (rather than sharp) onset of synchrony as coupling increases
3. Locking that dissolves under low-amplitude noise
4. If music substrate consistently scores > 0.05 below games/language,
   the single-invariant claim must be split into substrate-specific regimes

---

## Evidence

- `atlas/oscillator_locking.json` (source index, 3 runs, 100% pass rate)

Supporting runs:
- `oscillator_locking_20260315_041601_522c1d` (games, signal=0.9994) PASS
- `oscillator_locking_20260315_041604_705e4a` (language, signal=0.9998) PASS
- `oscillator_locking_20260315_041608_5b1924` (music, signal=0.9743) PASS

---

## Linked Experiments

- Probe: `labs/invariants/oscillator_locking_probe.py` (Phase 8 target)
- Follow-up: music substrate replication to resolve the 0.974 vs 0.999 gap
- Spatial replication: Phase 9 Godot engine

---

## Notes

Strongest raw signal of any current Helix invariant. Three runs is a thin
evidence base for Verified status — recommend 10+ run replication in Phase 8.
