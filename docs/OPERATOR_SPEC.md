# Helix Operator Specification

## Architecture Law

```
HSL → Operator → Adapter → Toolkit → Artifact → Atlas Compiler
```

## Core Operators (9)

| Operator | Purpose | Input | Output |
|----------|---------|-------|--------|
| `INGEST_TRACK` | Import raw data | File path + metadata | Parsed entity |
| `ANALYZE_TRACK` | Run analysis pipeline | Entity ID | Analysis artifacts |
| `COMPILE_ATLAS` | Compile to Atlas | Validated entities | Atlas entries |
| `DISCOVER` | Find structural patterns | Domain + parameters | Invariant candidates |
| `COMPARE` | Cross-entity comparison | Entity ID pair | Similarity metrics |
| `EXPLAIN` | Structural explanation | Entity ID | Explanation artifact |
| `LINK` | Create entity relationship | Entity ID pair + type | Relationship entry |
| `SEARCH` | Query Atlas | Search parameters | Matching entities |
| `STATUS` | System status report | None | Status dashboard |

## Operator Constraints

1. **No new operators** beyond the 9 defined above
2. Operators **orchestrate** — they do not perform domain-specific work
3. Operators **never write Atlas entities** directly
4. Direct toolkit calls from operators are **prohibited**
5. Toolkits writing artifacts or Atlas entities is **prohibited**
6. Monolithic pipelines (`master_pipeline.py`) are **prohibited**

## Operator Contract

Each operator must:
1. Accept typed input matching its specification
2. Route through the adapter layer for domain translation
3. Produce structured output conforming to entity schema
4. Return `Result` with success/failure status
5. Never modify state outside its designated artifact boundary
