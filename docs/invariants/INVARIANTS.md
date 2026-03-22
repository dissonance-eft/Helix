# Helix Invariants

## What is an Invariant?

An invariant is a structural law that holds across domains, representations, and perturbations.
Invariants are **discovered** (not declared) and must survive falsification to be promoted.

## Confidence Tiers

| Tier | Confidence | Requirements |
|------|------------|-------------|
| `CANDIDATE` | < 0.5 | Single observation, untested |
| `EMERGING` | 0.5–0.7 | 2+ runs, single domain |
| `STABLE` | 0.7–0.9 | Multi-domain, reproduced |
| `PROMOTED` | ≥ 0.9 | Passes 6-criterion promotion gate |
| `DEGRADED` | N/A | Failed reproducibility check |

## Named Invariants

### Decision Compression Principle (DCP)
Constrained systems generate structure by collapsing multiple possible futures into a smaller realized set through commitment or effectively irreversible narrowing.
- **Status:** `CANDIDATE`
- **Tier:** CANDIDATE → (needs null model run to reach EMERGING)
- **Domains observed:** games (86% pass rate, 3 domains), math (hook implemented), cognition (toy fixtures — heuristic only)
- **Key metrics:** `collapse_sharpness`, `tension_accumulation_index`, `possibility_space_entropy`, `collapse_morphology`
- **Authoritative doc:** `docs/invariants/decision_compression_principle.md` (v1.1)
- **Machine-readable:** `codex/library/invariants/decision_compression_principle.yaml` (v1.1)
- **Event schema:** `core/invariants/dcp/event.py` (dcp_event_v2 — adds collapse_morphology + constraint_class)
- **Morphology schema:** `core/invariants/dcp/morphology.py` (CollapseMorphology enum + profiles)
- **Math hook:** `domains/math/analysis/dcp.py`
- **Cognition fixtures:** `domains/cognition/fixtures/branching.py`, `domains/cognition/fixtures/attractor.py`
- **Research note:** `docs/research/dcp_trajectory_open_questions.md` (§7–§11)
- **Falsification priority:** F1 (null control collapse) must be run before any promotion

### Oscillator Locking
Synchronization emergence in coupled oscillator systems. The K_c transition in the Kuramoto model is the canonical math-domain expression of a DCP compression event.
- **Status:** `CANDIDATE` (105 occurrences, confidence 0.99 in atlas)
- **Domains observed:** math (formal fixture), games, music
- **Key metric:** order parameter R (`sync_index`)
- **Relationship to DCP:** Oscillator locking IS the math-domain DCP event. They are related but not identical — DCP is the general principle; oscillator locking is one instance.

### Epistemic Irreversibility Principle (EIP)
Knowledge acquisition as an irreversible structural transformation.
- Formalized proof: `proofs/` directory (separate repo)
- Key metric: eigenspace stability

## Invariant Lifecycle

```
Discovery → Candidate → Emerging → Stable → Promotion Gate → Promoted
                                                     ↓
                                               DEGRADED (if non-reproducible)
```

## Rules

1. No invariant may be **asserted** — only `invariant_candidates` are permitted
2. Each invariant requires evidence from **≥ 2 dialects** (e.g., causal + perceptual)
3. Invariants must be **representation-invariant** — discoverable across formats
4. All invariants undergo **adversarial validation** before promotion
