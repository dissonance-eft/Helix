# HIL Reference — Helix Interface Language v1.0

HIL is the formal command language for the Helix research platform.
It is not a chat interface, not a general-purpose language, and not
a shell wrapper. It is a constrained, typed, auditable DSL for
controlling experiment dispatch, atlas queries, system maintenance,
and graph traversal.

All experiment execution must enter through HIL. Direct shell invocation
of experiment scripts is blocked at the dispatcher and runner layers.

---

## Invocation

```bash
./helix "VERB [SUBCOMMAND] [typed-ref...] [key:value...]"
```

The `./helix` wrapper activates the venv and delegates to
`core/hil/hil_dispatch.py`. It is the only supported entry point
for HIL commands.

---

## Syntax

```
VERB [SUBCOMMAND] [typed-ref...] [key:value...]
```

All tokens are whitespace-separated. No parentheses, no operators,
no control flow. Order within targets and params does not matter —
roles are explicit in the prefix markers, not inferred from position.

### Quoting

Values containing `/`, spaces, or special characters must be quoted:

```
SYSTEM list path:"core/hil"
SYSTEM commit message:"Fix dispatch route"
OPERATOR log message:"Observed bistability at K=0.4"
```

Single or double quotes are both accepted:
```
SYSTEM commit message:'Enforce HIL pipeline'
```

---

## Typed References

The core semantic unit of HIL is the **typed reference**:

```
prefix:name
```

Where `prefix` is a known object type and `name` is the object ID.

| Prefix        | Object Class           | Atlas-backed |
|---------------|------------------------|:------------:|
| `invariant`   | Atlas invariant        | yes          |
| `experiment`  | Atlas experiment       | yes          |
| `model`       | Atlas model            | yes          |
| `regime`      | Atlas regime           | yes          |
| `operator`    | Atlas operator         | yes          |
| `parameter`   | Sweep parameter name   | no           |
| `engine`      | Execution engine       | no           |
| `artifact`    | Stored artifact file   | no           |
| `atlas`       | The atlas as a whole   | no           |
| `graph`       | The knowledge graph    | no           |
| `domain`      | Discovery domain       | no           |
| `atlas_entry` | Generic atlas entry    | no           |
| `graph_query` | Graph query object     | no           |

---

## Command Families

### RUN
Execute an experiment through the Python or Godot engine.

```
RUN experiment:epistemic_irreversibility engine:python
RUN experiment:oscillator_locking engine:python
RUN experiment:decision_compression engine:python repeat:5
RUN experiment:network_consensus engine:python
```

**Registered experiments** (defined in `engines/python/experiment_registry.py`):

| HIL name                    | Labs module                                           |
|-----------------------------|-------------------------------------------------------|
| `epistemic_irreversibility` | `labs.invariants.epistemic_irreversibility_probe`     |
| `decision_compression`      | `labs.invariants.decision_compression_probe`          |
| `oscillator_locking`        | `labs.invariants.oscillator_locking_probe`            |
| `local_incompleteness`      | `labs.invariants.local_incompleteness_probe`          |
| `regime_transition`         | `labs.invariants.regime_transition_probe`             |
| `network_consensus`         | `labs.network_consensus.experiment`                   |
| `oscillator_sync`           | `labs.oscillator_sync.experiment`                     |

New experiments must be added to `engines/python/experiment_registry.py`.
Running a script directly via shell is blocked.

---

### PROBE
Run a targeted probe against an invariant or experiment.

```
PROBE invariant:decision_compression
PROBE invariant:oscillator_locking
PROBE invariant:epistemic_irreversibility
```

---

### SWEEP
Sweep a parameter across a numeric range.

```
SWEEP parameter:coupling_strength range:0..1 steps:10 experiment:oscillator_locking
SWEEP parameter:noise range:0..0.5 steps:20 experiment:epistemic_irreversibility
SWEEP parameter:threshold range:0.1..0.9 steps:10
```

---

### COMPILE
Compile atlas entries, graph, or full pipeline.

```
COMPILE atlas
COMPILE graph
COMPILE entries
```

---

### INTEGRITY
Run the environment integrity verification suite before execution.

```
INTEGRITY check
INTEGRITY report
INTEGRITY gate
```

---

### ATLAS
Look up, list, or verify atlas entries.

```
ATLAS lookup invariant:decision_compression
ATLAS list
ATLAS status model:control_subspace_collapse
ATLAS verify invariant:oscillator_locking
```

---

### GRAPH
Query or export the Atlas Knowledge Graph.

```
GRAPH support invariant:decision_compression
GRAPH trace experiment:decision_compression_probe
GRAPH cluster
GRAPH build
GRAPH export
```

---

### VALIDATE
Validate atlas entries or experiments against HIL schemas.

```
VALIDATE atlas invariant:decision_compression
VALIDATE entry experiment:decision_compression_probe
VALIDATE invariant invariant:oscillator_locking
```

---

### TRACE
Trace the execution history of an experiment or artifact.

```
TRACE experiment:decision_compression_probe
TRACE experiment:epistemic_irreversibility
```

---

### OBSERVE
Passively observe an invariant or experiment without triggering execution.

```
OBSERVE invariant:decision_compression
OBSERVE experiment:epistemic_irreversibility
```

---

### REPORT
Generate a report on atlas objects or the knowledge graph.

```
REPORT summary invariant:decision_compression
REPORT full
REPORT graph
REPORT status
```

---

### EXPORT
Export Helix discoveries into external formats.

```
EXPORT atlas format:wiki
EXPORT graph
EXPORT wiki
```

---

### ANALYZE
Trigger post-hoc analysis of experiment artifacts.

```
ANALYZE atlas
ANALYZE patterns
ANALYZE features experiment:epistemic_irreversibility
```

---

### DISCOVER
Search for recurring patterns across validated experiments.

```
DISCOVER invariants domain:swarm
DISCOVER regimes
DISCOVER probes
```

---

### SYSTEM
Project management: git operations and file system tasks.
**This is the only way to perform git and file operations — no raw shell needed.**

#### Git operations

```
SYSTEM status                              # git status + disk usage
SYSTEM diff                                # git diff HEAD
SYSTEM log                                 # last 10 commits
SYSTEM log n:20                            # last N commits
SYSTEM add                                 # git add -A (stage everything)
SYSTEM add path:"core/hil/parser.py"       # stage a specific file
SYSTEM commit message:"Your message"       # commit only, no push
SYSTEM push                                # push to origin/main
SYSTEM pull                                # git pull
SYSTEM sync message:"Your message"         # add + commit + push (full sync)
```

#### File operations

```
SYSTEM list                                # list repo root
SYSTEM list path:"core/hil"               # list a subdirectory
SYSTEM mkdir path:"labs/new_experiment"   # create directory
SYSTEM move src:"temp/data" dest:"artifacts/data"
SYSTEM rename src:"old_name.py" dest:"new_name.py"
SYSTEM delete path:"artifacts/stale_run"  # delete file or directory
SYSTEM clean                               # remove __pycache__ trees
```

---

### OPERATOR
Manage operator context and the observation log.

```
OPERATOR log message:"Observed bistability at K=0.4"
OPERATOR status        # view last 500 chars of OPERATOR.md
OPERATOR profile       # view operator cognitive profile
```

---

## Parameters

| Param     | Type / Values         | Used by                        |
|-----------|-----------------------|--------------------------------|
| `engine`  | `python`, `godot`     | RUN, SWEEP, PROBE              |
| `range`   | `low..high` (floats)  | SWEEP                          |
| `steps`   | integer               | SWEEP                          |
| `repeat`  | integer               | RUN                            |
| `seed`    | integer               | RUN, SWEEP                     |
| `n`       | integer               | SYSTEM log                     |
| `verbose` | identifier            | INTEGRITY, VALIDATE, etc.      |
| `format`  | identifier            | REPORT, ATLAS, EXPORT          |
| `output`  | identifier            | REPORT, GRAPH                  |
| `depth`   | integer               | GRAPH, TRACE                   |
| `message` | quoted string         | SYSTEM commit/sync, OPERATOR   |
| `path`    | quoted string         | SYSTEM list/mkdir/delete       |
| `src`     | quoted string         | SYSTEM move/rename             |
| `dest`    | quoted string         | SYSTEM move/rename             |

---

## HIL Enforcement

All envelopes must carry `source="hil"` — set automatically by the
`dispatch_interface.py` pipeline. Any attempt to route an experiment
without this marker is rejected with status `HIL_REQUIRED`.

Enforcement points:
1. **`Dispatcher.route()`** — rejects non-HIL envelopes immediately
2. **`ExperimentRunner.run()`** — second check; rejects if source is not `"hil"`

This means the following are not supported and will return an error:
- Calling `ExperimentRunner.run()` directly with a hand-constructed dict
- Calling engine adapters directly
- Running `python3 labs/invariants/...` from shell

---

## Normalization

HIL normalizes semantically equivalent inputs to one canonical string.

| Input                             | Canonical                                        |
|-----------------------------------|--------------------------------------------------|
| `probe decision compression`      | `PROBE invariant:decision_compression`           |
| `run epistemic irreversibility`   | `RUN experiment:epistemic_irreversibility`       |
| `integrity`                       | `INTEGRITY check`                                |
| `compile the atlas`               | `COMPILE atlas`                                  |
| `compile atlas`                   | `COMPILE atlas`                                  |

Alias resolution runs before parsing. Aliases are registry-backed and
explicit — no fuzzy matching, no inference.

---

## Error Classes

| Error                    | Raised when                                            |
|--------------------------|--------------------------------------------------------|
| `HILSyntaxError`         | Tokenizer or parser cannot parse the input             |
| `HILValidationError`     | Parsed command fails semantic constraints              |
| `HILUnknownCommandError` | Verb not in command registry                           |
| `HILUnknownTargetError`  | Target name not found in atlas registry                |
| `HILUnsafeCommandError`  | Command contains a blocked safety pattern              |
| `HILAmbiguityError`      | Alias expansion matches multiple patterns              |

All error classes expose `.to_dict()` for structured logging.

Dispatch-level errors (not HIL parse errors):

| Status              | Meaning                                              |
|---------------------|------------------------------------------------------|
| `HIL_REQUIRED`      | Envelope did not originate from the HIL pipeline     |
| `HIL_INVALID`       | RUN/PROBE/SWEEP missing a required experiment target |
| `INVALID_ENVIRONMENT` | Integrity gate failed — not a real WSL2 environment |

---

## Validator Behavior

Checks run in order:

1. Known command family (verb in registry)
2. Subcommand required (per CommandSpec)
3. Target type validity (prefix in OBJECT_TYPES)
4. At least one target (if spec requires it)
5. Target type match (prefix in required_target_types)
6. Engine name validity
7. Range validity (low <= high, numeric)
8. Atlas registry lookup (if registry provided)
9. Defense-in-depth blocked patterns on canonical string (word-boundary matched)

---

## Safety Policy

The following patterns are unconditionally blocked at parse time and
re-checked on the canonical string at validation time:

- Shell commands: `rm`, `dd`, `mkfs`, `chmod`, `chown`, `wget`, `curl`, `sudo`
- SQL injection: `DROP`, `DELETE FROM`
- Device writes: `> /dev/`
- Python execution: `exec(`, `eval(`, `__import__`, `os.system`, `subprocess`

Rejection is immediate and raises `HILUnsafeCommandError`.

Pattern matching uses word boundaries for short alphabetic tokens to
prevent false positives (e.g. `dd` inside `add`).

---

## Command Logging

Every validated command is logged to `artifacts/hil_command_log.jsonl`.

Log record fields:
- `timestamp`          ISO-8601 UTC
- `original`           Raw input string
- `canonical`          Normalized HIL string
- `ast_summary`        Full parsed AST dict
- `targets`            List of typed reference strings
- `engine`             Resolved engine name
- `dispatch_route`     Inferred or explicit route
- `validation_status`  Always `"VALID"` for logged commands
- `integrity_gate`     `true` / `false` / `null`

---

## Dispatch Routes

| Verb        | Route                                          |
|-------------|------------------------------------------------|
| `RUN`       | `engines/python/` or `engines/godot/`          |
| `PROBE`     | `core/kernel/probe_runner` → `labs/invariants` |
| `SWEEP`     | `core/runner/sweep_runner`                     |
| `COMPILE`   | `core/compiler/atlas_compiler`                 |
| `INTEGRITY` | `core/integrity/integrity_tests`               |
| `ATLAS`     | `atlas/`                                       |
| `GRAPH`     | `core/graph/`                                  |
| `VALIDATE`  | `core/validator/`                              |
| `TRACE`     | `artifacts/`                                   |
| `SYSTEM`    | `core/kernel/system_handler`                   |
| `OPERATOR`  | `core/kernel/system_handler`                   |

---

## Compat API

Pre-Phase-11 callers can still use:

```python
from core.hil import parse_command, validate_command, normalize_command
```

These wrap the new system and return legacy dict formats.

---

## Package Structure

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
  hil_reference.md      This file — full language reference
  hil_influences.md     Design philosophy and language influences
  tests/
    test_parser.py
    test_normalizer.py
    test_validator.py
    test_aliases.py
    test_dispatch_interface.py
```
