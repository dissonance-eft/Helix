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

### Decision Compression
Structural compression of decision spaces under constraint.
- Domains observed: games, music
- Key metric: compression ratio

### Oscillator Locking
Synchronization emergence in coupled oscillator systems.
- Domains observed: music, games
- Key metric: order parameter R

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
