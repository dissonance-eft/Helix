# EIP — Epistemic Irreversibility Principle

## Purpose

EIP is a formal theory of survival constraints for bounded agents in environments containing irreversible terminal states.

Core claim: for any agent with finite epistemic capacity, there exists an informational horizon beyond which survival cannot be guaranteed without interactive state expansion.

## Status

Experimental. Active empirical testing underway.
Theory is provisional. Results are partial.

## Structure

```
notes/        Source theory, specifications, and proofs
claims/       Atomic claims extracted from notes (local staging)
experiments/  Experiment stubs and run records
```

Active Python experiment code: `experiments/eip/` (Helix root)
Validated KB objects: `kb/` (Helix root)

To promote a claim: place in `staging/` (Helix root) and run `python core/promote.py`.

## Integration with Helix

EIP uses Helix as a structural containment layer.
EIP claims are admitted to `kb/` only after passing schema and transition validation.
EIP does not modify core enforcement logic.
EIP is detachable without affecting Helix.

## Disclaimer

Helix hosts EIP as a modular experiment.
Helix does not endorse EIP.
Helix enforces structure. EIP provides content.
