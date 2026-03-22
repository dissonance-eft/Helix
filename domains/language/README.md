# HELIX LANGUAGE SUBSTRATE

**Version:** 1.1
**Status:** Authoritative target specification — see §11 for current implementation status
**Reference SPEC:** [SPEC.md](SPEC.md)

---

## 1. PURPOSE

The Language Substrate decomposes linguistic communication into its underlying structural invariants. It treats language not as a sequence of strings but as a hierarchical system of syntax, semantics, and constraints — a partially observable projection of author identity and conceptual structure.

---

## 2. ROLE WITHIN HELIX

The substrate provides the **Hierarchical Decomposition bridge** between Library input and Atlas output:

- **Input**: Textual datasets (`codex/library/language/`); lexicons, grammars, POS invariants
- **Engine**: 6-stage extraction — tokenization → syntax parse → semantic tagging → feature fusion
- **Output**: Sentence/concept entities and HelixEmbedding artifacts for Atlas compilation

---

## 3. COORDINATE SYSTEM SEPARATION

Two distinct axis systems exist. They are **not interchangeable**.

### A. Language-Domain Structural Signals (`LanguageStructuralSignals`)

Domain-local. Extracted from lexical, syntactic, and semantic layers of a text source. Does not directly enter the Atlas.

These signals are defined in full in [SPEC.md §1](SPEC.md). Key examples:

| Signal | Layer | Description |
|--------|-------|-------------|
| `phrasal_repetition_rate` | Syntactic | Frequency of recurring phrasal patterns |
| `inflectional_constraint` | Syntactic | Density of morphosyntactic markers |
| `clausal_nesting_depth` | Syntactic | Max level of subordinate clauses |
| `morpheme_density` | Lexical | Atomic meaning units per word |
| `lexical_diversity` | Lexical | Type-token ratio within analysis window |
| `topic_transition_smoothness` | Semantic | Cosine similarity between adjacent windows |

### B. Shared Cross-Domain Embedding (`HelixEmbedding`)

System-wide format. Required on all Atlas entities. Six axes: Complexity, Structure, Repetition, Density, Expression, Variation. All float in [0.0, 1.0].

Language-domain signals are projected into this format via the feature fusion stage (Stage 5). The mapping is explicit and domain-specific — see [SPEC.md §2](SPEC.md).

**Rule**: Never treat language signal names as equivalent to HelixEmbedding axis names. The mapping is deliberate, not implied.

---

## 4. PIPELINE (TARGET ARCHITECTURE)

```
Library Source (text datasets, lexicons, grammars)
    ↓
Ingestion (ingestion/)
    ↓  [raw text]
Tokenization → Syntax Parse → Semantic Tagging (feature_extraction/, structural_analysis/)
    ↓  [LanguageStructuralSignals]
Feature Fusion (pattern_detection/)
    ↓  [fused style vector]
HelixEmbedding Projection
    ↓  [HelixEmbedding]
Atlas Compilation
    ↓
Atlas (codex/atlas/language/)
```

6 stages in full — see [SPEC.md §3](SPEC.md).

---

## 5. ENTRY POINT

**Target**: HSL command (`INGEST_TRACK language.<id>`, `ANALYZE_TRACK language.<id>`)\
**Current**: Direct Python pipeline via `pipeline.py` (stub — raises NotImplementedError). Language domain has no implemented runtime path.

---

## 6. CONFIDENCE / CALIBRATION STATUS

Language-domain embeddings have no calibrated confidence procedure. The global provisional floor (0.30) applies as a system-wide minimum.

Domain-specific calibration would require:
1. A null corpus (randomized token sequences preserving surface ngram statistics)
2. Embedding distribution across null corpus
3. Floor set at `mean_null + 2 * std_null`

This calibration has not been performed.

---

## 7. FORMAL PRINCIPLES

Language provides a substrate for:

- **EIP (Epistemic Irreversibility Principle)**: Irreversible structural transformations in how a concept becomes encoded linguistically (e.g., lexical gap formation)
- **DCP (Decision Compression Principle)**: Compression of expressive choices under grammatical constraint (inflectional languages vs isolating)
- **LIP (Limited Inference / Constrained Inference)**: Recovery of underlying propositional invariant across surface-level language projections (translation)

---

## 8. CAPABILITIES (TARGET)

- **Decomposition**: Splitting sentences into parse trees and semantic frames
- **Mapping**: Projecting syntactic and semantic complexity into a single HelixEmbedding coordinate
- **Structural preservation**: Identifying when different languages (projections) express the same underlying structure (invariant)

---

## 9. CANONICAL FIXTURE

**Example: English ↔ Spanish structural alignment**

English: *"The quick brown fox jumps over the lazy dog"*\
Spanish: *"El veloz zorro marrón salta sobre el perro perezoso"*

Goal: demonstrate that while the surface dialects differ (lexical/syntactic), the underlying structural invariant (agent-action-target relationship) survives projection. Spanish's inflectional constraint increases `generative_constraint` while preserving `attractor_stability` of the core proposition.

**No formal validation harness exists yet** for this fixture. Deterministic fixture + null model guard: not yet implemented. See §12.

---

## 10. IMPLEMENTATION MILESTONES

| Milestone | Status |
|-----------|--------|
| **Canonical fixture defined** | ✅ Defined (EN ↔ ES alignment example) |
| **Domain runtime** | ❌ Pipeline is a stub |
| **Embedding generation** | ❌ Not implemented |
| **HSL entry point** | ❌ Not implemented |
| **Formal validation harness** | ❌ Not implemented |
| **Atlas persistence** | ❌ Not implemented |

---

## 11. CURRENT IMPLEMENTATION STATUS

| Component | Status |
|-----------|--------|
| Ingestion (`ingestion/`) | ⚠️ Directory exists; content unknown — not verified |
| Feature extraction (`feature_extraction/`) | ⚠️ Directory exists; content unknown |
| Pattern detection (`pattern_detection/`) | ⚠️ Directory exists; content unknown |
| Structural analysis (`structural_analysis/`) | ⚠️ Directory exists; content unknown |
| Full pipeline (`pipeline.py`) | ⚠️ Stub — raises NotImplementedError |
| Embedding generation | ❌ Not implemented |
| Domain validation harness (`validation/`) | ❌ Not implemented |
| HSL entry point | ❌ Not implemented |
| Null-baseline confidence calibration | ❌ Not performed |

---

## 12. KNOWN GAPS

- `pipeline.py` is a stub; no implemented runtime path exists
- No embedding generation for language domain
- No formal validation harness
- No null-model guard for language embedding
- Subdirectory contents (`ingestion/`, `feature_extraction/`, etc.) have not been verified as functional — status marked as unknown
- HSL does not route to the language domain
- Atlas persistence path does not exist

---

*For formal signal definitions, artifact schemas, and CCS derivation, see [SPEC.md](SPEC.md).*
