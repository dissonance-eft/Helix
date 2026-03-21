# Helix

**A closed-system invariant discovery engine.**

Helix is built around a single thesis: that structural laws exist beneath the surface of any domain, and that those laws can be recovered, validated, and made permanent. Every input — a sound chip register stream, a mathematical conjecture, a linguistic structure — is treated as a projection of an underlying invariant. Helix recovers those invariants under conditions of partial observability and compiles them into a verified, append-only knowledge base called the Atlas.

The system does not generalize loosely. It extracts precisely, validates strictly, and stores permanently.

> **"The representation is the window. The invariant is the target."**
>
> **[SYSTEM CONTEXT AUTHORITY]**: Helix is an integrated formal system. The documentation files linked in this repository are authoritative extensions of this README and constitute the complete architectural truth. No single document is sufficient in isolation. Any agent reading this file MUST read the linked documents to have an accurate model of the system.

---

## Canonical Pipeline

```
Library → HSL → Core → Atlas
```

| Layer | Path | Role |
|-------|------|------|
| **Library** | `codex/library/` | Raw priors — sound chips, artists, reference data. Unvalidated input material. |
| **HSL** | `core/hsl/` | Helix Structural Language — the only legal entry point into the system. All execution begins here. |
| **Core** | `core/` | The runtime: normalization, semantic modeling, operator execution, and atlas compilation. |
| **Atlas** | `codex/atlas/` | The output: compiled, validated, and append-only structural knowledge. |

All execution routes through **HSL → Operators → Atlas Compiler**. There are no direct Atlas writes. Every entity that enters the Atlas has passed normalization, schema validation, and compiler authorization. This is enforced at the runtime level, not by convention.

---

## Architecture

```
core/
├── hsl/           ← HSL parser + interpreter (only legal system entry)
├── compiler/      ← Atlas compilation pipeline (sole authorized Atlas writer)
├── kernel/        ← Dispatcher, runtime, graph engine, substrate guards
├── operators/     ← 9 core operators: INGEST, ANALYZE, DISCOVER, and 6 others
├── normalization/ ← Canonical ID enforcement (domain.type:slug format)
├── semantics/     ← Entity, property, and relationship registries
├── adapters/      ← Domain translation layer (music, math, games, ...)
├── enforcement/   ← Runtime checks, persistence gate, shadow audit
├── governance/    ← Validation rules, confidence tiers, promotion gates
├── integrity/     ← Root structure validation, artifact integrity checks
├── discovery/     ← Invariant discovery and candidate ranking
├── analysis/      ← Cross-probe and structural analysis utilities
├── models/        ← Internal data models and CCS representations
├── cli/           ← Command-line interface layer
└── bin/           ← Executable entry points

codex/
├── atlas/         ← Compiled invariants. Read-only post-commit.
└── library/       ← Priors and reference data. Not version-controlled.

domains/           ← Structured domain-specific pipelines (music, games, math, ...)

applications/      ← Domain-facing interface layer for downstream consumers
└── labs/          ← Research probes, live experiments, datasets
```

### Layer Responsibilities

**Library → HSL**: Raw material enters the library unvalidated. It is then parsed through HSL, which enforces the canonical entry point and rejects anything that does not conform to the system's structural language.

**Core**: The processing layer. Entities are normalized into canonical IDs, semantically indexed, operated on by one of the 9 core operators, and finally submitted to the compiler. The compiler is the only component authorized to write to the Atlas.

**Atlas**: The permanent record. Invariants are append-only and write-protected through the enforcement layer. Nothing enters the Atlas without passing the full pipeline.

**Enforcement Layer**: A runtime gate that intercepts all persistence attempts. The `enforce_persistence` function is the single canonical write path — it orchestrates authorization, validation, and atomic commit. The shadow audit system (`audit_system_state`) can scan the full Codex for existing state drift, schema violations, or corruption at any time.

---

## What Helix Is Not

- **Not a recommender** — Helix does not optimize for engagement. It extracts structural truth.
- **Not a metadata database** — Metadata is input material. Invariants are the actual output.
- **Not a storage system** — Helix analyzes and compiles. The Atlas stores. These are distinct responsibilities.
- **Not subjective** — Every observation must be evidence-backed and falsifiable across multiple domains before promotion.
- **Not a general-purpose framework** — Helix is purpose-built for invariant discovery within a closed, constraint-defined architecture. It is not designed to be extended casually.

---

## Authoritative System Documentation

The following documents constitute the full state of the Helix system. An agent or developer operating in this repository without reading them has an incomplete model of the system.

| Doc | Purpose |
|-----|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Layer model, data flow, and separation rules |
| [PIPELINE.md](docs/PIPELINE.md) | Step-by-step Library → Core → Atlas execution |
| [HSL.md](docs/HSL.md) | Helix Structural Language — full specification |
| [SPEC.md](docs/SPEC.md) | Complete technical specification |
| [ENTITY_SCHEMA.md](docs/ENTITY_SCHEMA.md) | Entity schema, canonical ID format, all 19 entity types |
| [OPERATOR_SPEC.md](docs/OPERATOR_SPEC.md) | All 9 core operators and their behavioral contracts |
| [GOVERNANCE.md](docs/GOVERNANCE.md) | Validation rules, confidence tiers, promotion gates |
| [INVARIANTS.md](docs/INVARIANTS.md) | Named invariants and their current confidence tiers |
| [STRUCTURE.md](core/STRUCTURE.md) | Architectural laws — brief, authoritative |
| [ENFORCEMENT.md](core/enforcement/ENFORCEMENT.md) | Centralized enforcement: persistence gate, shadow audit, failure policy |
| [DISSONANCE.md](docs/DISSONANCE.md) | Primary Operator Profile |
