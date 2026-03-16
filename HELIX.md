# HELIX

Helix is a structured discovery platform that runs disciplined experiments
across multiple substrates and compresses results into a unified knowledge atlas.

**Current Phase: 9 — Execution Verification System**
**Architecture Status: Stable**

---

## CORE PHILOSOPHY

Stable core. Flexible layers.

The core must remain minimal, deterministic, and constrained.
Exploratory systems and applications operate on top of the core.

Helix functions as a pattern discovery engine that:
1. Runs experiments across multiple substrates
2. Stores raw results in artifacts/
3. Compresses artifacts into structured Atlas knowledge
4. Verifies that execution is real, not simulated

**Immutable rules:**
- No upward imports from core
- Every experiment must produce a discrete artifact
- Atlas entries link to artifacts — never copy them
- All claims must be falsifiable
- Integrity verification before every experiment dispatch

---

## ARCHITECTURE (PHASE 9)

```
/helix
  /core
    /kernel        — execution kernel, dispatcher, HIL, runtime, governance
    /hil           — Helix Interface Language (parser, validator, normalizer)
    /validator     — atlas entry validation (atomicity, falsifiability, cross-ref)
    /integrity     — Phase 9: execution verification harness (5 probes)

  /engines
    /python        — Python experiment engine (network, dynamical, CA, evolutionary)
    /godot         — Godot spatial engine adapter (Phase 10)

  /labs
    /invariants    — probe implementations targeting specific invariants
    /simulation    — experiment scripts and sweep runners
    /cognition     — language and symbolic substrate experiments
    /creativity    — rhythmic and generative substrate experiments

  /atlas
    /invariants    — verified and exploratory invariant entries
    /experiments   — completed experiment records
    /models        — candidate explanatory structures
    /regimes       — identified system phases and states
    /operators     — reusable diagnostic and transformation tools
    /audits        — historical audit records
    /system_integrity — Phase 9 integrity run reports
    /docs          — architecture, philosophy, roadmap, HIL spec
    index.md       — full atlas index
    atlas_index.yaml — structured YAML registry

  /applications
    /eft           — Eigenspace Fragility Toolkit
    /rrs           — Repo Reliability Scanner
    /language_lab  — language substrate application
    /creativity_lab — creativity substrate application
    /game_systems_lab — game systems substrate application

  /artifacts       — raw experiment output (never edited, grows freely)
  /compiler        — atlas_compiler.py: artifacts -> atlas pipeline

  HELIX.md         — this file
  OPERATOR.md      — operator context and cognitive model
```

---

## EXECUTION PIPELINE (PHASE 9)

Every Helix experiment follows this pipeline:

```
OPERATOR COMMAND
      |
      v
  HIL PARSER          core/hil/
      |
      v
  VALIDATOR           core/hil/validator.py
      |
      v
  INTEGRITY GATE      core/integrity/integrity_tests.py
      |
      |-- FAIL --> HALT (artifact flagged INVALID_ENVIRONMENT)
      |
      v
  DISPATCHER          core/kernel/dispatcher/router.py
      |
      v
  ENGINE              engines/python/ or engines/godot/
      |
      v
  ARTIFACTS           artifacts/<run>/
      |
      v
  ATLAS COMPILER      compiler/atlas_compiler.py
      |
      v
  ATLAS               atlas/<type>/<entry>.md
                      atlas/atlas_index.yaml (updated)
                      atlas/index.md (updated)
```

---

## INTEGRITY SYSTEM (PHASE 9)

The integrity harness (`core/integrity/`) runs 5 probes before every experiment:

| Probe           | Tests                                              | Failure Meaning              |
|-----------------|----------------------------------------------------|------------------------------|
| environment     | WSL2 kernel signature in /proc/version             | Not running in real WSL2     |
| entropy         | Two /dev/urandom reads produce different output    | Execution may be simulated   |
| filesystem      | Sentinel file persists across sequential reads     | Filesystem not persistent    |
| hil             | HIL accepts valid / rejects invalid commands       | HIL enforcement broken       |
| sandbox         | Destructive commands blocked (rm -rf /, etc.)      | Sandbox breach               |

Run manually:
```
python3 core/integrity/integrity_tests.py
```

Results written to `atlas/system_integrity/<run_id>.md`.

**All 5 probes currently PASS on the active WSL2 environment.**

---

## ATLAS OBJECT TYPES

The Atlas stores 5 structured object types. Raw data never lives in the Atlas.

| Type       | Description                              | Directory              |
|------------|------------------------------------------|------------------------|
| Invariant  | Cross-domain structural rule             | atlas/invariants/      |
| Experiment | Completed falsification test + results   | atlas/experiments/     |
| Model      | Candidate explanatory structure          | atlas/models/          |
| Regime     | Identified phase or system state         | atlas/regimes/         |
| Operator   | Reusable diagnostic/transformation tool  | atlas/operators/       |

All entries use the Phase 8 schema:
- Title, Type, Status, Origin
- Domain Coverage
- Mechanism
- Predictions
- Falsifiers (required — no entry without falsifiers)
- Evidence (links to artifacts, never copies)
- Linked Experiments
- Notes

---

## CURRENT ATLAS STATE

### Verified Invariants

**Decision Compression** — `atlas/invariants/decision_compression.md`
- Status: Verified (7/7 runs, mean signal 0.434)
- Substrates: Games, Language, Music
- Next: Spatial replication via Godot engine (Phase 10)
- Linked model: Control Subspace Collapse

**Oscillator Locking** — `atlas/invariants/oscillator_locking.md`
- Status: Verified (3/3 runs, mean signal 0.991)
- Substrates: Games, Language, Music
- Open question: Music signal (0.974) vs Games/Language (0.999) gap
- Recommendation: 10+ run replication in Phase 8

### Exploratory Invariants (Probes Pending)

- **Epistemic Irreversibility** — information-theoretic irreversibility at belief commits
- **Local Incompleteness** — local rule consistency does not imply global completeness
- **Regime Transition** — sharp phase boundaries in parameter space

### Seeded Entries

- **Experiment:** Decision Compression Sweep (`atlas/experiments/decision_compression_sweep.md`)
- **Model:** Control Subspace Collapse (`atlas/models/control_subspace_collapse.md`)
- **Operator:** Commitment Probe (`atlas/operators/commitment_probe.md`)

---

## LAYER RULES

```
core/          — stable, minimal, rarely changes
               — kernel, HIL, validator, integrity
               — no imports from engines/, labs/, applications/

engines/       — modular execution substrates
               — imports from core/ only
               — add new engines without touching core/

labs/          — active experimentation zone
               — imports from core/ and engines/
               — may be unstable; core/ is not

atlas/         — read-only compressed knowledge
               — written by compiler/ only
               — never manually insert raw data

applications/  — user-facing systems
               — import from core/ only
               — must never modify core/

artifacts/     — raw output, grows freely
               — never edited after write
               — source material for atlas compiler
```

---

## HIL (HELIX INTERFACE LANGUAGE)

All Helix commands normalize through HIL before execution.

HIL components in `core/hil/`:
- `grammar.py` — command grammar and syntax rules
- `normalizer.py` — command normalization
- `validator.py` — validation pipeline (accepts/rejects commands)
- `dispatch_interface.py` — dispatch routing interface

Valid HIL commands:
```
PROBE <target>
RUN <experiment>
SWEEP <parameter_space>
COMPILE atlas
INTEGRITY check
```

Destructive commands are rejected at the HIL layer before reaching the dispatcher.

---

## PHASE LOG

| Phase | Name                             | Status    |
|-------|----------------------------------|-----------|
| 1–5   | Pre-stabilization research       | Complete  |
| 6     | Architecture stabilization       | Complete  |
| 7     | Atlas Compiler (artifact->atlas) | Complete  |
| 8     | Atlas Consolidation System       | Complete  |
| 9     | Execution Verification System    | Complete  |
| 10    | Atlas Knowledge Graph            | Next      |
| 11    | Adversarial Validation Probes    | Planned   |
| 12    | Module Expansion                 | Planned   |

---

## DESIGN PRINCIPLES

1. **Artifact-first**: No claim exists outside a discrete, reproducible artifact
2. **Falsifiability required**: Every atlas entry must specify conditions under which it fails
3. **Layered authority**: Core is immutable; labs may be unstable
4. **Compression**: Artifacts -> Atlas is lossy by design. Only structure survives
5. **Cross-substrate**: A pattern appearing in one substrate is a hypothesis; across three is a candidate invariant
6. **Integrity before execution**: Real environments produce real results; simulated environments produce nothing

---

## RUNNING HELIX

```bash
# Integrity check
python3 core/integrity/integrity_tests.py

# Compile artifacts into atlas
python3 compiler/atlas_compiler.py

# Run a specific probe
python3 labs/invariants/decision_compression_probe.py

# View atlas index
cat atlas/index.md
```

---

*Helix is a constrained discovery environment.*
*The Atlas is its memory.*
*The Core is its foundation.*
