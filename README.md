# Helix

**A closed-system invariant discovery engine.**

Helix discovers structural laws that hold across domains, representations, and perturbations. Every input — a sound chip register stream, a mathematical conjecture, a linguistic structure — is treated as a projection of an underlying invariant. Helix recovers those invariants under conditions of partial observability.

> **"The representation is the window. The invariant is the target."**

---

## Canonical Pipeline

```
Library → HSL → Core → Atlas
```

| Layer | Path | Role |
|-------|------|------|
| **Library** | `codex/library/` | Raw priors — sound chips, artists, reference data. Unvalidated. |
| **HSL** | `core/hsl/` | Helix Structural Language — the only legal entry point |
| **Core** | `core/` | Normalization → Semantics → Operators → Compiler |
| **Atlas** | `codex/atlas/` | Compiled, validated, structural knowledge. Append-only. |

All execution routes through **HSL → Operators → Atlas Compiler**. No direct Atlas writes.

---

## Architecture

```
core/
├── hsl/           ← HSL parser + interpreter
├── compiler/      ← Atlas compilation pipeline (only Atlas writer)
├── kernel/        ← Dispatcher, runtime, graph, substrate guards
├── normalization/ ← ID enforcement (domain.type:slug)
├── semantics/     ← Entity, property, relationship registries
├── operators/     ← 9 core operators (INGEST, ANALYZE, DISCOVER, ...)
├── adapters/      ← Domain translation layer
└── governance/    ← Validation, promotion gates, audit

codex/
├── atlas/         ← Compiled invariants (read-only)
└── library/       ← Priors and reference data (not version-controlled)

domains/           ← Structured domain pipelines (music, games, ...)
labs/              ← Research probes, experiments, datasets
```

---

## What Helix Is Not

- **Not a recommender** — structural truth, not engagement
- **Not a metadata database** — invariants are the target, metadata is secondary
- **Not a storage system** — Helix analyzes; the Atlas stores
- **Not subjective** — every observation must be evidence-backed and falsifiable

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layer model, data flow, separation rules |
| [PIPELINE.md](docs/PIPELINE.md) | Library → Core → Atlas execution stages |
| [HSL.md](docs/HSL.md) | Helix Structural Language specification |
| [SPEC.md](docs/SPEC.md) | Full technical specification |
| [ENTITY_SCHEMA.md](docs/ENTITY_SCHEMA.md) | Entity schema, ID format, 19 entity types |
| [OPERATOR_SPEC.md](docs/OPERATOR_SPEC.md) | 9 core operators and their contracts |
| [GOVERNANCE.md](docs/GOVERNANCE.md) | Validation rules, promotion gates |
| [INVARIANTS.md](docs/INVARIANTS.md) | Named invariants, confidence tiers |
| [STRUCTURE.md](core/STRUCTURE.md) | Architectural laws (brief) |
| [ENFORCEMENT.md](core/enforcement/ENFORCEMENT.md) | Centralized enforcement authority |
