# Invariant: Decision Compression

**Type:** Invariant
**Status:** Verified
**Origin:** Helix cross-domain probe — games, language, music
**Confidence:** Verified (7/7 runs, mean signal 0.434)
**Last Updated:** 2026-03-15

---

## Domain Coverage

- Games (discrete competitive systems)
- Language (sequential symbolic systems)
- Music (temporal rhythmic structures)
- Spatial substrate: pending (Phase 9)

---

## Mechanism

As a system approaches an irreversible commitment event, the effective
dimensionality of its decision space contracts. Influence vectors that
previously spanned a high-dimensional action space collapse into a
low-dimensional control subspace. The system's degrees of freedom
compress before the decision is finalized — not after.

This compression is observable as a measurable signal in the structure
of influence distributions immediately prior to commitment.

---

## Predictions

1. Signal > 0.35 in any substrate with genuine irreversible commitment events
2. Signal strength correlates positively with commitment irreversibility
3. Compression occurs pre-commitment, not post
4. Pattern should appear in Godot spatial simulations with multi-agent
   commitment dynamics (testable Phase 9)

---

## Falsifiers

1. Any substrate with genuine commitment events showing signal < 0.20
2. Signal that increases *after* commitment rather than before
3. High-dimensional action space that does not contract pre-commitment
4. Cross-domain failure: pattern in games but not language under identical
   probe parameters falsifies the invariant claim

---

## Evidence

- `atlas/decision_compression.json` (source index, 7 runs, 100% pass rate)
- `artifacts/experiments/dcp_discovery/`
- `artifacts/experiments/cross_domain_compression/`

Supporting runs:
- `decision_compression_20260315_040912_9b9715` (games, signal=0.4649) PASS
- `decision_compression_20260315_040916_72dd2a` (language, signal=0.3938) PASS
- `decision_compression_20260315_040916_7c0ec2` (music, signal=0.4273) PASS
- `decision_compression_20260315_042458_8672e2` (games, signal=0.4649) PASS

---

## Linked Experiments

- Probe: `labs/invariants/decision_compression_probe.py` (Phase 8 target)
- Spatial replication: Phase 9 Godot engine

---

## Notes

Highest-priority verified invariant in the Atlas. Spatial validation via
Godot engine (Phase 9) is the next falsification target. Signal variance
across substrates (0.39–0.46) warrants substrate-sensitivity analysis.
