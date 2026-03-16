# HELIX

**Repository:** [github.com/dissonance-eft/Helix](https://github.com/dissonance-eft/Helix)

Helix is a structured discovery platform that runs disciplined experiments
across multiple substrates and compresses results into a unified knowledge atlas.

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
5. Accepts all operator commands through a formal, auditable control language (HIL)

**Immutable rules:**
- No upward imports from core
- Every experiment must produce a discrete artifact
- Atlas entries link to artifacts — never copy them
- All claims must be falsifiable
- Integrity verification before every experiment dispatch
- All commands enter through HIL — no raw dispatch

---

## ARCHITECTURE

```
/helix
  /core
    /kernel        — execution kernel, dispatcher, runtime, governance
    /hil           — Helix Interface Language (full formal package)
    /validator     — atlas entry validation
    /integrity     — execution verification harness
    /graph         — Atlas Knowledge Graph
    /analysis      — automated analysis suite (migrated)
    /compiler      — atlas_compiler.py: artifacts -> atlas pipeline (migrated)
    /validation    — adversarial validation layer (migrated)

  /engines
    /python        — Python experiment engine
    /godot         — Godot spatial engine adapter

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
    atlas_index.json — structured knowledge registry

  /interface
    /wiki          — Atlas Interface & Wiki Export (from atlas_interface)
    /apps          — User-facing systems (rrs, language_lab, etc.)

  /artifacts       — raw experiment output (append-only)

  HELIX.md         — this file
  OPERATOR.md      — operator context and cognitive model
  ROADMAP.md       — system vision and future modules
```

---

## EXECUTION PIPELINE

Every Helix experiment follows this pipeline:

```
OPERATOR COMMAND
      |
      v
  ALIAS RESOLUTION    core/hil/aliases.py
      |                 (human shorthand -> canonical HIL)
      v
  HIL PARSER          core/hil/parser.py
      |                 (canonical string -> HILCommand AST)
      v
  VALIDATOR           core/hil/validator.py
      |                 (AST semantic + safety checks)
      v
  COMMAND LOGGER      core/hil/command_logger.py
      |                 (record to artifacts/hil_command_log.jsonl)
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
  ATLAS COMPILER      core/compiler/atlas_compiler.py
      |
      v
  ATLAS               atlas/<type>/<entry>.md
                      atlas/atlas_index.yaml (updated)
                      atlas/atlas_graph.json (updated)
```

---

## HIL — HELIX INTERFACE LANGUAGE

HIL is the formal command language for Helix. It is not a prompt parser,
not a chat wrapper, and not a shell alias system. It is a typed, auditable,
formally-grammared DSL with a real parser, AST, and validator.

### Package structure

```
core/hil/
  grammar.ebnf          Formal EBNF grammar (canonical reference)
  parser.py             Tokenizer + recursive-descent parser -> HILCommand AST
  ast_nodes.py          HILCommand, TypedRef, RangeExpr dataclasses
  normalizer.py         Alias resolution + parse + canonical() output
  validator.py          Semantic validation of parsed AST
  dispatch_interface.py Parse -> validate -> log -> dispatcher bridge
  command_logger.py     Logs every validated command to artifact record
  aliases.py            Registry-backed alias -> canonical HIL table
  command_registry.py   CommandSpec for every verb family
  ontology.py           OBJECT_TYPES, ATLAS_BACKED_TYPES, VALID_ENGINES
  semantic_roles.py     SemanticRole enum + COMMAND_ROLE_MAP
  errors.py             Structured error hierarchy
  hil_dispatch.py       Full pipeline CLI entry point
  hil_reference.md      Full language reference
  hil_influences.md     Design philosophy and language influences
  tests/
    test_parser.py
    test_normalizer.py
    test_validator.py
    test_aliases.py
    test_dispatch_interface.py
```

### Command syntax

```
VERB [SUBCOMMAND] [typed-ref...] [key:value...]
```

Typed references are the core semantic unit:
```
prefix:name     e.g.  invariant:decision_compression
                      experiment:decision_compression_probe
                      parameter:coupling_strength
                      engine:python
```

---

## INTEGRITY SYSTEM

The integrity harness (`core/integrity/`) runs standard probes before every experiment:

| Probe       | Tests                                           | Failure Meaning            |
|-------------|------------------------------------------------|----------------------------|
| environment | WSL2 kernel signature in /proc/version         | Not running in real WSL2   |
| entropy     | Two /dev/urandom reads differ                  | Execution may be simulated |
| filesystem  | Sentinel file persists across reads            | Filesystem not persistent  |
| hil         | HIL accepts valid / rejects invalid commands   | HIL enforcement broken     |
| sandbox     | Destructive commands blocked (rm -rf /, etc.)  | Safety policy breach       |

---

## ATLAS KNOWLEDGE GRAPH

The atlas graph is auto-built by `core/compiler/atlas_compiler.py`.

Current state: **11 nodes, 11 edges** (Updated with Epistemic Irreversibility)

Files:
- `atlas/atlas_graph.json` — serialized graph
- `atlas/atlas_graph.dot` — Graphviz export

---

## ATLAS OBJECT TYPES

| Type       | Description                              | Directory              |
|------------|------------------------------------------|------------------------|
| Invariant  | Cross-domain structural rule             | atlas/invariants/      |
| Experiment | Completed falsification test + results   | atlas/experiments/     |
| Model      | Candidate explanatory structure          | atlas/models/          |
| Regime     | Identified phase or system state         | atlas/regimes/         |
| Operator   | Reusable diagnostic/transformation tool  | atlas/operators/       |

All entries use the established schema: Title, Type, Status, Origin, Domain Coverage,
Mechanism, Predictions, Falsifiers, Evidence, Linked Experiments, Notes.

---

## CURRENT ATLAS STATE

### Verified Invariants

**Decision Compression** — `atlas/invariants/decision_compression.md`
- Status: Verified (7/7 runs, mean signal 0.434)
- Substrates: Games, Language, Music

**Oscillator Locking** — `atlas/invariants/oscillator_locking.md`
- Status: Verified (3/3 runs, mean signal 0.991)
- Substrates: Games, Language, Music

### Exploratory Invariants

**Epistemic Irreversibility** — `atlas/invariants/epistemic_irreversibility.md`
- Status: Candidate (1/1 HIL runs, mean signal 49.8 bits)
- Domain: Dynamical Systems (Bistable COMMIT)

**Local Incompleteness** — local rule consistency does not imply global completeness
**Regime Transition** — sharp phase boundaries in parameter space

---

## LAYER RULES

```
core/          — stable, minimal, rarely changes
               — kernel, HIL, validator, integrity, graph
               — no imports from engines/, labs/, applications/

engines/       — modular execution substrates
               — imports from core/ only

labs/          — active experimentation zone
               — imports from core/ and engines/
               — may be unstable; core/ is not

atlas/         — read-only compressed knowledge
               — written by compiler/ only

interface/     — human interface layers
               — imports from core/ only

artifacts/     — raw output, grows freely; never edited after write
```

---

## DESIGN PRINCIPLES

1. **Artifact-first**: No claim exists outside a discrete, reproducible artifact
2. **Falsifiability required**: Every atlas entry must specify conditions under which it fails
3. **Layered authority**: Core is immutable; labs may be unstable
4. **Compression**: Artifacts -> Atlas is lossy by design. Only structure survives
5. **Cross-substrate**: A pattern across three substrates is a candidate invariant
6. **Integrity before execution**: Real environments produce real results
7. **HIL-first**: All commands enter through the formal HIL pipeline — no raw dispatch

---

## RUNNING HELIX

All experiment execution must go through the HIL wrapper.

```bash
# Issue a HIL command
./helix "PROBE invariant:epistemic_irreversibility"

# Run a specific experiment with parameters
./helix "RUN experiment:network_consensus engine:python p:0.4"

# Perform a parameter sweep
./helix "SWEEP parameter:noise range:0..0.5 steps:10 RUN experiment:epistemic_irreversibility"

# Compile artifacts into atlas + rebuild graph
./helix "COMPILE atlas"

# Run full HIL test suite
python3 -m pytest core/hil/tests/ -v
```

---

*Helix is a constrained discovery environment.*
*The Atlas is its memory.*
*The Core is its foundation.*
*HIL is its voice.*

---

## REPOSITORY ARCHITECTURE RULES

The Helix root directory contains only top-level system layers.

Allowed root entries:
- `core/`
- `labs/`
- `engines/`
- `atlas/`
- `interface/`
- `artifacts/`
- `HELIX.md`
- `OPERATOR.md`
- `ROADMAP.md`
- `helix` (CLI wrapper)

All functional modules must exist under `core/`.
No additional folders may be added to the root without architectural review.
Artifacts are append-only and must never be modified automatically.
