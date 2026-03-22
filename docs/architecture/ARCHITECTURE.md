# Helix Architecture

## Layer Model

```
┌─────────────────────────────────────────────────────┐
│                    HSL / CLI                        │  Entry point
├─────────────────────────────────────────────────────┤
│              Normalization Gate                      │  ID enforcement
├─────────────────────────────────────────────────────┤
│              Semantics Layer                         │  Type resolution
├─────────────────────────────────────────────────────┤
│              Operator Registry                       │  Execution dispatch
├─────────────────────────────────────────────────────┤
│              Adapter Layer                           │  Domain translation
├─────────────────────────────────────────────────────┤
│              Atlas Compiler                          │  Knowledge compilation
├─────────────────────────────────────────────────────┤
│              Atlas (codex/atlas/)                    │  Compiled truth (read-only)
└─────────────────────────────────────────────────────┘
```

## Canonical Data Flow

```
Library (codex/library/)     →  priors, reference models, raw data
        ↓
Core (HSL → Operators)       →  normalization, semantics, execution
        ↓
Atlas (codex/atlas/)         →  compiled, validated knowledge (append-only)
```

## Directory → Layer Mapping

| Directory       | Layer           | Role |
|----------------|-----------------|------|
| `core/hsl/`     | Entry           | HSL parser, interpreter, grammar |
| `core/normalization/` | Gate      | ID format enforcement |
| `core/semantics/` | Resolution    | Entity/property/relationship registries |
| `core/operators/` | Execution     | Operator dispatch + builtins |
| `core/adapters/`  | Translation   | Domain-specific adapters |
| `core/compiler/`  | Compilation   | Atlas compiler pipeline |
| `codex/atlas/`    | Knowledge     | Compiled semantic knowledge (sacred, append-only) |
| `codex/library/`  | Priors        | Unvalidated reference models |
| `domains/`        | Pipelines     | Domain-specific analysis (music, language, math, games) |
| `applications/labs/` | Research    | Probes, experiments, datasets |
| `applications/`    | Output        | Tools and interfaces built on Helix invariants |
| `core/governance/` | Governance    | Validation rules, audit, promotion gates |

## Layer Separation Rules

1. **No upward writes**: Labs cannot write to Core. Core cannot write to Atlas directly.
2. **Single writer**: Only `core/compiler/atlas_compiler.py` writes to `codex/atlas/`.
3. **HSL is the only entry point**: All execution routes through HSL → Operators.
4. **Library ≠ Atlas**: Library = incomplete priors. Atlas = validated posteriors.
5. **Domains ≠ Labs**: Domains = structured pipelines. Labs = exploratory experiments.

## ID Format

All entity IDs use colon-separated format: `domain.type:slug`

Examples:
- `music.artist:yuzo_koshiro`
- `music.track:streets_of_rage_2_go_straight`
- `tech.sound_chip:yamaha_ym2612`
