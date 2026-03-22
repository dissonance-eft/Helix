# HELIX GAMES SUBSTRATE

**Version:** 2.1
**Status:** Authoritative target specification — see §11 for current implementation status
**Reference SPEC:** [SPEC.md](SPEC.md)

---

## 1. PURPOSE

The Games Substrate extracts the latent decision architecture underlying gameplay. Games provide controlled adversarial systems with fully observable replay logs, deterministic state, and measurable decision pressure — making them ideal research subjects for Helix invariant discovery.

Scope: replay log ingestion, game state reconstruction, strategy and policy analysis, decision compression metric extraction, artifact generation. Not a game engine, training framework, or development toolkit.

---

## 2. ROLE WITHIN HELIX

The substrate provides the **Decision Structure Extraction bridge** between Library input and Atlas output:

- **Input**: Game replays, agent logs, simulation outputs (`codex/library/games/`)
- **Engine**: 6-stage pipeline — ingestion → state reconstruction → strategy analysis → feature extraction → pattern detection → artifact generation
- **Output**: Game entity artifacts → Atlas Compiler → Atlas (codex/atlas/games/)

The Games domain is a **primary test bed** for Helix invariants. Games provide the cleanest experimental conditions for initial detection of `decision_compression` and `oscillator_locking`.

---

## 3. COORDINATE SYSTEM SEPARATION

Two distinct axis systems exist. They are **not interchangeable**.

### A. Games-Domain Structural Signals (`GamesStructuralSignals`)

Domain-local. Extracted from game state trajectories and agent decision sequences. Does not directly enter the Atlas.

Key signals:

| Signal | Stage | Description |
|--------|-------|-------------|
| `decision_entropy_slope` | Feature | Rate of entropy reduction approaching decision point |
| `phase_coherence` | Feature | Degree of synchronization at steady state (multi-agent) |
| `policy_entropy` | Feature | Shannon entropy of action distribution at decision point |
| `action_distribution` | Feature | Per-agent action frequency per game phase |
| `strategy_cluster_id` | Pattern | k-means cluster assignment over policy vectors |
| `equilibrium_flag` | Pattern | Detected stable strategy equilibrium |
| `policy_collapse_flag` | Pattern | Detected convergence to degenerate strategy |

### B. Shared Cross-Domain Embedding (`HelixEmbedding`)

System-wide format. Required on all Atlas entities. Six axes: Complexity, Structure, Repetition, Density, Expression, Variation. All float in [0.0, 1.0].

Games-domain signals project into this format via the artifact preparation layer. The mapping is explicit and domain-specific — see [SPEC.md §2](SPEC.md).

**Rule**: Never treat games signal names as equivalent to HelixEmbedding axis names. The mapping is deliberate, not implied.

---

## 4. PIPELINE (TARGET ARCHITECTURE)

```
Game Replays / Agent Logs
    ↓
Ingestion + Parsing (Stage 1)
    ↓  [canonical game event format]
State Reconstruction (Stage 2)
    ↓  [game state graph, agent state transitions]
Strategy Analysis (Stage 3)
    ↓  [policy inference, decision tree reconstruction]
Feature Extraction (Stage 4)
    ↓  [GamesStructuralSignals]
Pattern Detection (Stage 5)
    ↓  [strategy clusters, equilibria, phase transitions]
Artifact Generation (Stage 6)
    ↓  [artifacts/games/<session_id>/]
Atlas Compilation
    ↓
Atlas (codex/atlas/games/)
```

**Operator orchestration**:
```
RUN operator:SCAN substrate:games
RUN operator:ANALYZE entity:game.session:<id>
RUN operator:COMPILE_ATLAS
```

---

## 5. ENTRY POINT

**Target**: HIL/HSL commands — `RUN operator:SCAN substrate:games`, `PROBE invariant:decision_compression lab:games`\
**Current**: Direct Python pipeline via `pipeline.py` (partial stub). No implemented runtime extraction path in `godot_engine/` subdirectory beyond structural scaffolding.

HIL command syntax is defined (see §4 and [SPEC.md §9](SPEC.md)) but not fully implemented.

---

## 6. CONFIDENCE / CALIBRATION STATUS

Games-domain invariant confidence is based on observed pass rate across runs. Active probe results:

| Probe | Status | Pass Rate | Domains |
|-------|--------|-----------|---------|
| `decision_compression` | Verified | 86% | 3 |
| `oscillator_locking` | Verified | 100% | 3 |

**Note**: These verification statuses are from previous experimental runs. The governance promotion criteria (6-criterion gate) applies. Confidence thresholds for embedding are global provisional (0.30) and not domain-calibrated.

---

## 7. FORMAL PRINCIPLES

Games provide the primary empirical substrate for:

- **DCP (Decision Compression Principle)**: Policy entropy drops sharply approaching irreversible moves — the clearest cross-domain DCP signal
- **EIP (Epistemic Irreversibility Principle)**: Game decision points as canonical irreversible state transitions
- **Oscillator Locking**: Multi-agent coordination emergence in cooperative games — cross-domain signal alongside math/music

---

## 8. CAPABILITIES (TARGET)

- Replay log ingestion and canonical game event parsing
- Game state reconstruction from replay sequences
- Strategy and policy analysis via decision tree reconstruction
- Decision compression metric extraction (DCP signal)
- Pattern detection: equilibria, strategy clusters, policy collapse, coordination emergence
- Cross-game invariant validation via labs

---

## 9. CANONICAL FIXTURE

**Active probes**: `decision_compression` and `oscillator_locking`

Both probes have been verified at multi-domain level (86% and 100% pass rates, 3 domains each). These are the most empirically grounded invariants in the Helix system.

Probe datasets:
- `applications/labs/datasets/games/decision_compression_dataset.json`
- `applications/labs/datasets/games/oscillator_locking_dataset.json`

**No formal validation harness exists yet** under `domains/games/validation/`. The existing verification happened through lab probes, not through a Helix-native domain validation fixture. See §12.

---

## 10. IMPLEMENTATION MILESTONES

| Milestone | Status |
|-----------|--------|
| **Canonical fixture defined** | ✅ Two active probes with verified pass rates |
| **Domain architecture** | ✅ Well-specified — entity types, artifact schemas, pipeline stages |
| **Domain runtime** | ⚠️ Partial — `godot_engine/` dir present; pipeline stub only |
| **HSL/HIL entry point** | ⚠️ Defined in spec; implementation status unknown |
| **Formal validation harness** | ❌ Not implemented under `domains/games/validation/` |
| **Atlas persistence** | ⚠️ Defined in spec; enforcement gate integration not confirmed |

---

## 11. CURRENT IMPLEMENTATION STATUS

| Component | Status |
|-----------|--------|
| Pipeline architecture (`pipeline.py`) | ⚠️ Partial stub |
| Game engine adapter (`godot_engine/`) | ⚠️ Directory present; content not verified |
| Ingestion | ❌ Not implemented |
| State reconstruction | ❌ Not implemented |
| Strategy analysis | ❌ Not implemented |
| Feature extraction | ❌ Not implemented |
| Pattern detection | ❌ Not implemented |
| Domain validation harness (`validation/`) | ❌ Not implemented |
| HSL/HIL orchestration | ⚠️ Defined; not confirmed implemented |
| Null-baseline confidence calibration | ❌ Not performed |

---

## 12. KNOWN GAPS

- No implemented runtime extraction path (pipeline is a stub)
- No formal domain validation harness under `domains/games/validation/`
- Dataset path references in old docs used `labs/games/` — canonical path is `applications/labs/datasets/games/`
- Repository structure in old docs referenced `substrates/games/` — actual path is `domains/games/`
- HIL/HSL orchestration is specified but runtime implementation not confirmed
- Probe verification (86%/100%) reflects past lab runs, not a current validated harness

---

*For formal signal definitions, entity schemas, artifact schemas, and promotion conditions, see [SPEC.md](SPEC.md).*
