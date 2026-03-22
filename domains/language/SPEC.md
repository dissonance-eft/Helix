# HELIX LANGUAGE SUBSTRATE SPECIFICATION

**Version:** 1.1
**Status:** Authoritative target specification — implementation status tracked in README.md §11
**Relationship:** Extends `domains/language/README.md`

---

## 1. DOMAIN SCOPE

The Language Substrate operates across three primary layers:
- **Lexical**: Discrete tokens, morphemes, and their surface properties
- **Syntactic**: Phrasal arrangement rules, parse structure, dependency relations
- **Semantic**: Underlying conceptual structure, thematic roles, topic coherence

Its goal is to identify structural identity — recurring patterns of phrasal construction and conceptual mapping that define an author, dialect, or language family — and extract invariants that survive translation or register shift.

---

## 2. DOMAIN-LOCAL STRUCTURAL SIGNALS

These signals are extracted by the language pipeline and are domain-local. They are NOT the same as HelixEmbedding axes. They feed into the feature fusion stage which produces a shared embedding.

### 2.1 Lexical Signals
- **`morpheme_density`**: Atomic units of meaning per word
- **`lexical_diversity`**: Type-token ratio (TTR) within analysis window
- **`phonetic_entropy`**: Distribution variation of phonemes (spoken corpora only)

### 2.2 Syntactic Signals
- **`phrasal_depth`**: Maximum depth of the constituent parse tree
- **`dependency_length`**: Cumulative linear distance between governors and dependents
- **`inflectional_constraint`**: Density of morphosyntactic markers (gender, number, tense)
- **`phrasal_repetition_rate`**: Frequency of recurring phrasal patterns

### 2.3 Semantic Signals
- **`topic_cohesion`**: Semantically related vectors per unit text
- **`argument_structure_complexity`**: Count of thematic roles correctly filled
- **`topic_transition_smoothness`**: Cosine similarity between adjacent semantic windows

---

## 3. SHARED EMBEDDING PROJECTION

Language-domain signals are fused and projected into the shared `HelixEmbedding` format.

**Projection mapping** (signal → embedding axis):

| HelixEmbedding Axis | Primary Language Signal | Normalization Method |
|---------------------|-------------------------|----------------------|
| `structure` | `phrasal_repetition_rate` | Baseline: news corpus idiom density |
| `complexity` | `inflectional_constraint` | Scale of grammatical rule-boundness |
| `repetition` | `clausal_nesting_depth` | Max level of subordinate clauses |
| `density` | `morpheme_density` | Tokens/morphemes per semantic unit |
| `variation` | `lexical_diversity` | Author-specific vocabulary variance |
| `expression` | `topic_transition_smoothness` | Cosine similarity between adjacent windows |

**Non-equivalence rule**: HelixEmbedding axis names are system-wide. Language signal names are domain-local. The mapping is explicit and not a naming equivalence.

**Projection schema versioning**: A `projection_schema` field should be stamped on all language embedding artifacts. Not yet implemented.

---

## 4. PIPELINE STAGES

| Stage | Responsibility | Input | Output | Status |
|-------|----------------|-------|--------|--------|
| 1 | Ingestion | Raw text | Language index entry | ❌ Not implemented |
| 2 | Tokenization | Text stream | Tokens / morphemes | ❌ Not implemented |
| 3 | Syntax parse | Token stream | Parse tree / dependency graph | ❌ Not implemented |
| 4 | Semantic tagging | Parse tree | Semantic roles / frames | ❌ Not implemented |
| 5 | Feature fusion | All layers | LanguageStyleVector | ❌ Not implemented |
| 6 | Atlas compilation | Artifacts | Atlas entities | ❌ Not implemented |

---

## 5. ARTIFACT SCHEMAS

### SyntacticProfile (`artifacts/language/<id>/syntax.json`)
```json
{
  "sentence_id": "...",
  "parse_tree_depth": 14,
  "dependency_graph": {},
  "constraint_indices": {}
}
```

### SemanticFrame (`artifacts/language/<id>/semantics.json`)
```json
{
  "sentence_id": "...",
  "thematic_roles": {
    "agent": "fox",
    "action": "jumps",
    "target": "dog"
  }
}
```

### HelixEmbedding (`artifacts/language/<id>/embedding.json`)
```json
{
  "complexity": 0.65,
  "structure": 0.82,
  "repetition": 0.44,
  "density": 0.31,
  "expression": 0.22,
  "variation": 0.76,
  "confidence": 0.61,
  "domain": "language",
  "source_vector": "language_style_vector",
  "projection_schema": "language_v1"
}
```

---

## 6. VALIDATION RULES

- **Translation preservation check** (target): A sentence translated to a different language must maintain cross-substrate alignment score > 0.80 for its semantic invariants — not yet validated
- **Model invariance** (target): Syntactic depth measurements must be consistent across parser adapters (SpaCy vs NLTK) — not yet validated
- **Null model guard** (target): Randomized token sequences must not produce embeddings above confidence floor — not yet implemented

---

## 7. METRIC SPACE / SIMILARITY / DISTANCE

The HelixEmbedding metric space uses Euclidean distance normalized by √6:

```
distance(a, b) = euclidean(a, b) / sqrt(6)          ∈ [0, 1]
similarity(a, b) = 1 - distance(a, b)               ∈ [0, 1]
```

**Triangle inequality** applies to **distance**, not similarity:
```
d(a, c) ≤ d(a, b) + d(b, c)
```

A violation is a `STRUCTURAL_FAILURE`.

---

## 8. ENTRY / HSL INTEGRATION STATE

**Target**: HSL commands `INGEST_TRACK language.<id>`, `ANALYZE_TRACK language.<id>`\
**Current**: `pipeline.py` is a stub. No HSL route exists. No runtime path implemented.

---

## 9. THRESHOLDS AND CALIBRATION

| Threshold | Value | Status |
|-----------|-------|--------|
| Minimum embedding confidence | 0.30 | Provisional — global default, not language-calibrated |
| Translation alignment floor | 0.80 | Defined; calibration basis unknown |

Calibration procedure for confidence floor: generate null corpus (random token sequences) → compute embedding distribution → set at `mean + 2 * std`. Not yet performed.

---

## 10. PROMOTION CONDITIONS

Invariant candidates must pass the global 6-criterion promotion gate (see `docs/GOVERNANCE.md`). No language-domain candidates have been promoted or are in active pipeline.

---

## 11. KNOWN ASSUMPTIONS / OPEN CONSTRAINTS

- Language domain assumes Unicode text input with sentence boundary detection
- Syntactic models assume English primarily; cross-lingual support requires per-language adapter
- Translation invariant (0.80 floor) is a target value without empirical basis
- All pipeline stages are stubs or unverified — this spec describes the target state, not current state
- `projection_schema` versioning not yet implemented
