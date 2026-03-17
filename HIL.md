============================================================
HELIX INTERFACE LANGUAGE (HIL) SPECIFICATION
============================================================

Document Type: Language Specification
System: Helix
Version: 1.0
Purpose: Defines the Helix Interface Language used to interact
with the Helix research system.

Scope: HIL provides the structured command interface used by
operators and automated agents to control the Helix environment.

This document defines:

• the HIL command grammar
• the typed reference system
• command families and execution semantics
• dispatch behavior
• validation rules
• safety constraints
• repository integration points


------------------------------------------------------------
1. PURPOSE OF HIL
------------------------------------------------------------

The Helix Interface Language (HIL) is a constrained command
language used to interact with the Helix system.

HIL is not:

• a conversational interface
• a general-purpose programming language
• a shell wrapper

HIL is a typed, auditable DSL designed to control:

• experiment execution
• Atlas queries
• graph traversal
• pipeline dispatch
• repository management
• operator interaction

All experiments executed within Helix must pass through HIL.

Direct invocation of experiment scripts is intentionally blocked
to preserve reproducibility and provenance tracking.


------------------------------------------------------------
2. DESIGN PRINCIPLES
------------------------------------------------------------

HIL is designed according to several principles.

Explicit Structure

Commands must explicitly name their targets and parameters.

AST-First Parsing

Commands are parsed into a structured AST before execution.

Deterministic Behavior

Invalid commands fail immediately and explicitly.

Typed References

All system objects are addressed through typed identifiers.

Protocol-Style Semantics

Commands behave like structured packets rather than natural
language instructions.

Reproducibility

Every validated command is logged as a structured artifact.


------------------------------------------------------------
3. COMMAND GRAMMAR
------------------------------------------------------------

HIL commands follow the canonical structure:

VERB [SUBCOMMAND] [typed-ref...] [key:value...]

Example commands:

RUN experiment:decision_compression engine:python

PROBE invariant:oscillator_locking

SWEEP parameter:noise range:0..0.5 steps:20 experiment:epistemic_irreversibility

ATLAS lookup invariant:decision_compression

GRAPH trace experiment:decision_compression_probe

SYSTEM commit message:"Update experiment registry"


------------------------------------------------------------
4. TYPED REFERENCES
------------------------------------------------------------

The fundamental addressing mechanism of HIL is the typed reference.

prefix:name

Examples:

experiment:decision_compression
invariant:oscillator_locking
engine:python
parameter:noise
artifact:run_2026_03_17

Typed references allow commands to be order-independent while
preserving explicit semantic roles.

Recognized prefixes:

invariant
experiment
model
regime
operator
parameter
engine
artifact
atlas
graph
domain
atlas_entry
graph_query


------------------------------------------------------------
5. COMMAND FAMILIES
------------------------------------------------------------

HIL commands are organized into families.

RUN

Execute an experiment through a runtime engine.

Example:

RUN experiment:decision_compression engine:python


PROBE

Run a targeted probe against an invariant.

Example:

PROBE invariant:decision_compression


SWEEP

Perform a parameter sweep.

Example:

SWEEP parameter:coupling_strength range:0..1 steps:10 experiment:oscillator_locking


ATLAS

Interact with the Atlas knowledge graph.

Example:

ATLAS lookup invariant:decision_compression
ATLAS list
ATLAS verify invariant:oscillator_locking


GRAPH

Query Atlas relationships.

Example:

GRAPH support invariant:decision_compression
GRAPH trace experiment:decision_compression_probe


VALIDATE

Validate Atlas entries and experiments.

Example:

VALIDATE atlas invariant:decision_compression


TRACE

Trace execution history.

Example:

TRACE experiment:decision_compression_probe


REPORT

Generate system reports.

Example:

REPORT summary invariant:decision_compression


EXPORT

Export Atlas knowledge.

Example:

EXPORT atlas format:wiki


ANALYZE

Run artifact analysis.

Example:

ANALYZE features experiment:epistemic_irreversibility


DISCOVER

Search for recurring structural patterns.

Example:

DISCOVER invariants domain:swarm


SYSTEM

Repository and environment management.

Examples:

SYSTEM status
SYSTEM commit message:"Update parser"
SYSTEM push


OPERATOR

Operator context and observation log.

Example:

OPERATOR log message:"Observed bistability at K=0.4"


------------------------------------------------------------
6. PARAMETER SYSTEM
------------------------------------------------------------

Parameters follow the format:

key:value

Examples:

engine:python
range:0..1
steps:20
seed:42
format:wiki


------------------------------------------------------------
7. COMMAND EXECUTION PIPELINE
------------------------------------------------------------

HIL commands pass through the following pipeline.

User Command
    ↓
Tokenizer
    ↓
Parser
    ↓
AST Representation
    ↓
Validator
    ↓
Command Logger
    ↓
Dispatcher
    ↓
Subsystem Execution
    ↓
Artifact Generation
    ↓
Atlas Integration


------------------------------------------------------------
8. COMMAND LOGGING
------------------------------------------------------------

All validated commands are logged to:

artifacts/hil_command_log.jsonl

Log records include:

timestamp
original_input
canonical_command
ast_summary
targets
engine
dispatch_route
validation_status


------------------------------------------------------------
9. SAFETY POLICY
------------------------------------------------------------

HIL blocks potentially destructive commands.

Blocked patterns include:

rm
dd
mkfs
sudo
curl
wget
DROP
DELETE FROM
exec(
eval(

Commands containing these tokens are rejected before execution.


------------------------------------------------------------
10. REPOSITORY INTEGRATION
------------------------------------------------------------

The HIL implementation lives within:

core/hil/

core/hil/

grammar.ebnf
parser.py
ast_nodes.py
normalizer.py
validator.py
dispatch_interface.py
command_logger.py
aliases.py
command_registry.py
ontology.py
semantic_roles.py
errors.py
hil_dispatch.py


------------------------------------------------------------
11. RELATIONSHIP TO HELIX ARCHITECTURE
------------------------------------------------------------

HIL is the operational interface of Helix.

It connects the system layers:

Specification
    ↓
HIL Interface
    ↓
Core Services
    ↓
Substrate Pipelines
    ↓
External Tools
    ↓
Artifacts
    ↓
Atlas Knowledge Graph


------------------------------------------------------------
12. DESIGN INFLUENCES
------------------------------------------------------------

HIL draws from several design traditions.

SQL

Explicit target addressing and verb-object structure.

Lisp

AST-first parsing and composable primitives.

Unix

Small deterministic commands and explicit failure.

Workflow DSLs

Reproducible research pipelines and parameter sweeps.

Graph Query Systems

Relationship-oriented commands.

Telecommunications Protocols

Packet-style command structure with explicit fields.


------------------------------------------------------------
END OF HIL SPECIFICATION
------------------------------------------------------------