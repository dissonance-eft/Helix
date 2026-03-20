# Helix Execution Pipeline

## Canonical Flow

```
Library → HSL → Normalization → Semantics → Operators → Adapter → Atlas Compiler → Atlas
```

## Stages

### 1. Library (`codex/library/`)
Raw priors: artist definitions, album metadata, sound chip specs, source files.
Library data is **unvalidated** — it represents collected reference material.

### 2. HSL Entry (`core/hsl/`)
All execution begins with an HSL command. The interpreter parses input and dispatches to the appropriate operator.

### 3. Normalization (`core/normalization/`)
- Enforces `domain.type:slug` ID format via `id_enforcer.py`
- Validates input structure before semantic processing

### 4. Semantics (`core/semantics/`)
- Resolves entity types against `entity_types.py` (19 types)
- Validates properties against `property_types.py` (50+ specs)
- Checks relationships against `relationship_types.py` (30+ specs)

### 5. Operators (`core/operators/`)
- 9 core operators: `INGEST_TRACK`, `ANALYZE_TRACK`, `COMPILE_ATLAS`, `DISCOVER`, `COMPARE`, `EXPLAIN`, `LINK`, `SEARCH`, `STATUS`
- Operators orchestrate but do not perform domain-specific work

### 6. Adapters (`core/adapters/`)
- Translate between domain-specific formats and the universal entity schema
- Each domain (music, language, math, games) may provide its own adapter

### 7. Atlas Compiler (`core/compiler/atlas_compiler.py`)
- The ONLY module authorized to write to `codex/atlas/`
- Validates entity completeness, schema conformance, CCS embedding presence
- Generates `registry.json` index

### 8. Atlas (`codex/atlas/`)
- Compiled, validated, semantic knowledge
- **Append-only**: existing entries are never overwritten
- **Compiler-gated**: no direct writes permitted

## Phase Separation Rules

- `INGEST` must not trigger analysis
- `ANALYZE` must not modify metadata
- Partial entities may exist with `analysis_status: pending`
- Attribution inference is always a falsifiable hypothesis
