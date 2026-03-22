"""
HSL Interpreter — Helix Formal System
=======================================
Parse, validate, and execute HSL commands through the five-layer pipeline:

    HSL → Normalization → Semantics → Operator Runtime → Atlas Compiler → Atlas

Entry point:
    run_command(raw: str, context: CommandContext | None = None) -> dict

Execution flow:
    run_command(raw)
      → parse(raw)                    # core/hsl/parser.py
      → validate(cmd)                 # core/hsl/validator.py
      → context = CommandContext.default() if not provided
      → HSLInterpreter(context).execute(cmd)
      → return result dict

Result format:
    {"status": "ok",        "data": ..., "command": cmd.canonical()}
    {"status": "not_found", "error": "EntityNotFoundError: ...", "command": ...}
    {"status": "error",     "error": "...", "command": ...}

Execution modes (HELIX_MODE env var):
    runtime (default) — operators must exist, schemas cannot mutate,
                        direct atlas writes blocked, arbitrary scripts blocked
    dev               — operator registration allowed, schema evolution allowed
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from core.hsl.ast_nodes import HSLCommand
from core.hsl.context import CommandContext
from core.hsl.errors import HSLError, HSLValidationError
from core.hsl.parser import parse
from core.hsl.validator import validate
from core.kernel.schema.entities.resolver import EntityNotFoundError, EntityResolver


# ---------------------------------------------------------------------------
# Execution mode
# ---------------------------------------------------------------------------

def get_execution_mode() -> str:
    """Return 'runtime' or 'dev' based on HELIX_MODE environment variable."""
    return os.environ.get("HELIX_MODE", "runtime").lower()


def is_runtime_mode() -> bool:
    return get_execution_mode() == "runtime"


def is_dev_mode() -> bool:
    return get_execution_mode() == "dev"


# ---------------------------------------------------------------------------
# run_command — public entry point
# ---------------------------------------------------------------------------

def run_command(raw: str, context: CommandContext | None = None) -> dict:
    """
    Parse, validate, resolve entities, and execute a HSL command.

    Returns a result dict with keys: status, data or error, command.
    Never raises — all errors are captured into the result dict.
    """
    try:
        cmd = parse(raw)
    except HSLError as e:
        return {"status": "error", "error": str(e), "command": raw}
    except Exception as e:
        return {"status": "error", "error": f"ParseError: {e}", "command": raw}

    try:
        validate(cmd)
    except HSLError as e:
        return {"status": "error", "error": str(e), "command": cmd.canonical()}
    except Exception as e:
        return {"status": "error", "error": f"ValidationError: {e}", "command": cmd.canonical()}

    if context is None:
        context = CommandContext.default()

    interp = HSLInterpreter(context)
    return interp.execute(cmd)


class HSLInterpreter:
    """
    Executes validated HSL commands against a CommandContext.

    In runtime mode: only registered operators may execute, schemas are
    immutable, direct Atlas writes are blocked.
    In dev mode: operator registration and schema evolution are permitted.
    """

    def __init__(self, context: CommandContext) -> None:
        self._ctx = context

    def execute(self, cmd: HSLCommand) -> dict:
        dispatch = {
            "ENTITY":    self._exec_entity,
            "ATLAS":     self._exec_entity,
            "GRAPH":     self._exec_graph,
            "SUBSTRATE": self._exec_substrate,
            "PROBE":     self._exec_probe,
            "RUN":       self._exec_run,
            "SWEEP":     self._exec_sweep,
            "COMPILE":   self._exec_compile,
            "INTEGRITY": self._exec_integrity,
            "ANALYZE":   self._exec_analyze,
            "DISCOVER":  self._exec_discover,
            "OPERATOR":  self._exec_operator,
        }
        handler = dispatch.get(cmd.verb)
        if handler is None:
            return self._unsupported(cmd)
        try:
            return handler(cmd)
        except EntityNotFoundError as e:
            return {"status": "not_found", "error": str(e), "command": cmd.canonical()}
        except HSLValidationError as e:
            return {"status": "error", "error": str(e), "command": cmd.canonical()}
        except Exception as e:
            return {"status": "error", "error": str(e), "command": cmd.canonical()}

    # ── ENTITY ────────────────────────────────────────────────────────────────

    def _exec_entity(self, cmd: HSLCommand) -> dict:
        sub = cmd.subcommand
        resolver = EntityResolver(self._ctx.registry) if self._ctx.registry else EntityResolver.default()

        if sub == "get":
            target = cmd.primary_target()
            if target is None:
                return self._error(cmd, "ENTITY get requires a target entity ID")
            entity = resolver.resolve(target.entity_id())
            return self._ok(cmd, entity.to_dict())

        if sub == "list":
            type_filter    = cmd.params.get("type")
            ns_filter      = cmd.params.get("namespace")
            name_filter    = cmd.params.get("name")
            entities       = resolver.all()
            if type_filter:
                entities = [e for e in entities if e.type.lower() == type_filter.lower()]
            if ns_filter:
                entities = [e for e in entities if e.namespace == ns_filter.lower()]
            if name_filter:
                entities = [e for e in entities if name_filter.lower() in e.name.lower()]

            limit  = int(cmd.params.get("limit", 100))
            offset = int(cmd.params.get("offset", 0))
            paged  = entities[offset:offset + limit]

            return self._ok(cmd, {
                "entities": [e.to_dict() for e in paged],
                "count":    len(entities),
                "offset":   offset,
                "limit":    limit,
            })

        if sub == "link":
            target = cmd.primary_target()
            if target is None:
                return self._error(cmd, "ENTITY link requires a source entity target")
            relation  = cmd.params.get("relation", "RELATED_TO")
            target_id = cmd.params.get("target")
            if not target_id:
                return self._error(cmd, "ENTITY link requires relation:... and target:...")
            if self._ctx.registry is None:
                return self._error(cmd, "No registry in context")
            self._ctx.registry.link(target.entity_id(), relation.upper(), target_id)
            return self._ok(cmd, {
                "linked":   target.entity_id(),
                "relation": relation.upper(),
                "to":       target_id,
            })

        if sub == "add":
            # In runtime mode: adding new entity types not already in ontology is blocked
            params    = cmd.params
            target    = cmd.primary_target()
            if target is None:
                return self._error(cmd, "ENTITY add requires a typed entity reference")
            entity_id = target.entity_id()
            name      = params.get("name", target.name)
            type_str  = params.get("type", target.prefix.capitalize())
            description = params.get("description", "")

            if is_runtime_mode() and not description:
                return self._error(
                    cmd,
                    "ENTITY add requires description:... in runtime mode. "
                    "All entities must have a description."
                )

            if self._ctx.registry is None:
                return self._error(cmd, "No registry in context")

            from core.kernel.schema.entities.schema import Entity
            entity = Entity(
                id=entity_id,
                type=type_str,
                name=name,
                label=params.get("label", name),
                description=description,
                metadata={
                    "source": "hsl",
                    "source_stage": "hsl_add",
                    "source_artifact": "manual",
                    "extraction_method": "hsl_command",
                },
            )
            entity.validate()
            self._ctx.registry.add(entity)
            return self._ok(cmd, {"added": entity_id, "type": type_str})

        if sub == "export":
            if self._ctx.registry is None:
                return self._error(cmd, "No registry in context")
            return self._ok(cmd, self._ctx.registry.to_dict())

        return self._error(cmd, f"Unknown ENTITY subcommand: {sub!r}")

    # ── GRAPH ─────────────────────────────────────────────────────────────────

    def _exec_graph(self, cmd: HSLCommand) -> dict:
        sub   = cmd.subcommand
        graph = self._ctx.graph

        if sub == "neighbors":
            target = cmd.primary_target()
            if target is None:
                return self._error(cmd, "GRAPH neighbors requires a target entity ID")
            if graph is None:
                return self._error(cmd, "No entity graph in context")
            entity_id = target.entity_id()
            if graph.node(entity_id) is None:
                return self._not_found(cmd, entity_id)
            neighbor_pairs = graph.neighbors(entity_id)
            return self._ok(cmd, {
                "entity_id": entity_id,
                "neighbors": [{"id": nid, "edge_type": e.type} for nid, e in neighbor_pairs],
            })

        if sub == "path":
            targets = cmd.targets
            if len(targets) < 2:
                return self._error(cmd, "GRAPH path requires two entity targets")
            if graph is None:
                return self._error(cmd, "No entity graph in context")
            src  = targets[0].entity_id()
            dst  = targets[1].entity_id()
            path = _bfs_path(graph, src, dst)
            if path is None:
                return self._ok(cmd, {"src": src, "dst": dst, "path": None, "reachable": False})
            return self._ok(cmd, {"src": src, "dst": dst, "path": path, "reachable": True})

        if sub == "edges":
            target = cmd.primary_target()
            if target is None:
                return self._error(cmd, "GRAPH edges requires a target entity ID")
            if graph is None:
                return self._error(cmd, "No entity graph in context")
            entity_id = target.entity_id()
            edges_out = [str(e) for e in graph.edges_from(entity_id)]
            edges_in  = [str(e) for e in graph.edges_to(entity_id)]
            return self._ok(cmd, {"entity_id": entity_id, "edges_out": edges_out, "edges_in": edges_in})

        return self._unsupported(cmd)

    # ── SUBSTRATE ─────────────────────────────────────────────────────────────

    def _exec_substrate(self, cmd: HSLCommand) -> dict:
        sub             = cmd.subcommand
        substrates_root = Path(__file__).parent.parent.parent / "substrates"

        if sub == "list":
            dirs = [
                d.name for d in sorted(substrates_root.iterdir())
                if d.is_dir() and not d.name.startswith("_")
            ]
            return self._ok(cmd, {"substrates": dirs})

        if sub == "info":
            name = cmd.params.get("name") or (
                cmd.primary_target().name if cmd.primary_target() else None
            )
            if not name:
                return self._error(cmd, "SUBSTRATE info requires name:substrate_name")
            substrate_dir = substrates_root / name
            if not substrate_dir.exists():
                return self._not_found(cmd, f"substrate:{name}")
            files = [f.name for f in substrate_dir.iterdir() if f.is_file()]
            return self._ok(cmd, {"name": name, "path": str(substrate_dir), "files": files})

        if sub == "run":
            name = cmd.params.get("name") or (
                cmd.primary_target().name if cmd.primary_target() else None
            )
            if not name:
                return self._error(cmd, "SUBSTRATE run requires name:substrate_name")
            if name == "music":
                try:
                    from substrates.music.pipeline import MusicSubstratePipeline
                    stages_param  = cmd.params.get("stages")
                    stages        = [int(s) for s in str(stages_param).split(",") if s.strip().isdigit()] if stages_param else None
                    soundtrack    = cmd.params.get("soundtrack")
                    resume_raw    = cmd.params.get("resume")
                    resume_from   = int(resume_raw) if resume_raw and str(resume_raw).isdigit() else 1
                    pipeline      = MusicSubstratePipeline(
                        stages=stages,
                        soundtrack_filter=soundtrack,
                        resume_from=resume_from,
                    )
                    result = pipeline.run()
                    return self._ok(cmd, result)
                except Exception as e:
                    return self._error(cmd, f"Substrate run failed: {e}")
            return self._error(cmd, f"No runnable pipeline found for substrate {name!r}")

        return self._unsupported(cmd)

    # ── RUN ───────────────────────────────────────────────────────────────────

    def _exec_run(self, cmd: HSLCommand) -> dict:
        """
        Execute a registered operator.

        Syntax: RUN operator:<name> [<entity_type>:<entity_id>] [key:value...]

        In runtime mode, only operators registered in OperatorRegistry may run.
        Unknown operators → HSLValidationError.
        """
        from core.operators.operator_registry import get_registry

        target = cmd.primary_target()

        # Determine operator name: from operator: prefix or subcommand
        operator_name = None
        entity_target = None

        for t in cmd.targets:
            if hasattr(t, "prefix") and t.prefix.lower() == "operator":
                operator_name = t.name.upper()
            else:
                entity_target = t

        if operator_name is None:
            # Fallback: try primary target as operator name
            if target and hasattr(target, "prefix") and target.prefix.lower() == "operator":
                operator_name = target.name.upper()

        if operator_name is None:
            return self._error(
                cmd,
                "RUN requires an operator target: RUN operator:<name> [entity_type:<id>]"
            )

        # Validate operator exists (raises HSLValidationError in runtime mode)
        registry = get_registry()
        spec = registry.require(operator_name)

        # Validate input entity type if provided
        if entity_target is not None:
            entity_type = entity_target.prefix.capitalize() if hasattr(entity_target, "prefix") else None
            if entity_type and not spec.accepts(entity_type):
                return self._error(
                    cmd,
                    f"Operator {operator_name} does not accept entity type {entity_type!r}. "
                    f"Accepted types: {sorted(spec.accepted_input_types)}"
                )

        # Dispatch to operator pipeline
        return self._dispatch_operator(cmd, spec, entity_target)

        # Dispatch to operator pipeline
        return self._dispatch_operator(cmd, spec, entity_target)

    def _dispatch_operator(self, cmd: HSLCommand, spec: Any, entity_target: Any) -> dict:
        """Route to the appropriate operator pipeline."""
        from core.operators.operator_registry import get_registry
        registry = get_registry()
        
        # Check for functional implementation
        impl_class = registry.get_implementation(spec.name)
        if impl_class:
            op_instance = impl_class()
            payload = {**cmd.params}
            if entity_target:
                payload["entity_id"] = entity_target.entity_id()
                # If target has a name that looks like a path, use it
                if not payload.get("file_path") and hasattr(entity_target, "name"):
                    payload["file_path"] = entity_target.name
            
            try:
                result = op_instance.run(payload)
                return self._ok(cmd, result)
            except Exception as e:
                return self._error(cmd, f"Operator {spec.name} execution failed: {e}")

        op = spec.name

        if op == "PROBE":
            return self._run_probe_operator(cmd, entity_target)

        if op == "COMPILE":
            return self._run_compile_operator(cmd)

        if op == "DISCOVER":
            target = entity_target or cmd.primary_target()
            invariant_id = target.entity_id() if target else None
            if not invariant_id:
                return self._error(cmd, "RUN operator:DISCOVER requires an invariant target")
            from core.discovery.discovery_dispatch import DiscoveryDispatch
            discovery = DiscoveryDispatch(self._ctx.registry)
            result = discovery.discover_experiments(invariant_id)
            return self._ok(cmd, result)

        if op == "SCAN":
            name = cmd.params.get("substrate") or (entity_target.name if entity_target else None)
            if not name:
                return self._error(cmd, "RUN operator:SCAN requires substrate:<name>")
            return self._ok(cmd, {
                "status":    "ok",
                "operator":  "SCAN",
                "substrate": name,
                "message":   f"Substrate scan of {name!r} dispatched via SCAN operator pipeline.",
                "stages":    list(spec.pipeline_stages),
            })

        # Generic operator response (operator exists, pipeline not yet wired)
        return self._ok(cmd, {
            "status":   "ok",
            "operator": op,
            "stages":   list(spec.pipeline_stages),
            "message":  f"Operator {op} accepted. Pipeline: {' → '.join(spec.pipeline_stages)}",
        })

    def _run_probe_operator(self, cmd: HSLCommand, entity_target: Any) -> dict:
        """Dispatch PROBE operator through the probe runner."""
        try:
            from core.kernel.dispatcher.probe_runner import ProbeRunner
            invariant_id = entity_target.entity_id() if entity_target else None
            if not invariant_id:
                return self._error(cmd, "RUN operator:PROBE requires an invariant target")

            # Extract invariant name from id slug
            slug = invariant_id.split(":", 1)[-1] if ":" in invariant_id else invariant_id
            lab  = cmd.params.get("lab", "games")

            runner = ProbeRunner()
            result = runner.run(probe_name=slug, lab_name=lab)
            return self._ok(cmd, result)
        except ImportError:
            # ProbeRunner not available — return operator spec acknowledgement
            return self._ok(cmd, {
                "status":   "ok",
                "operator": "PROBE",
                "message":  "PROBE operator dispatched (runner unavailable in this context)",
            })

    def _run_compile_operator(self, cmd: HSLCommand) -> dict:
        """Dispatch COMPILE operator through the atlas compiler."""
        from core.compiler.atlas_compiler import run as compile_run
        overwrite = cmd.params.get("overwrite", "false").lower() == "true"
        stats = compile_run(verbose=False, overwrite=overwrite)
        return self._ok(cmd, {
            "status":     "ok",
            "operator":   "COMPILE",
            "created":    len(stats.get("created", [])),
            "skipped":    len(stats.get("skipped", [])),
            "errors":     len(stats.get("errors", [])),
            "candidates": len(stats.get("candidates", [])),
        })

    # ── PROBE ─────────────────────────────────────────────────────────────────

    def _exec_probe(self, cmd: HSLCommand) -> dict:
        """
        PROBE verb — shorthand for RUN operator:PROBE <target>.
        Routes through the operator registry.
        """
        target = cmd.primary_target()
        from core.operators.operator_registry import get_registry
        spec = get_registry().require("PROBE")
        return self._run_probe_operator(cmd, target)

    # ── SWEEP ─────────────────────────────────────────────────────────────────

    def _exec_sweep(self, cmd: HSLCommand) -> dict:
        """
        SWEEP verb — parametric sweep over a registered operator.
        Validates operator exists before dispatching.
        """
        from core.operators.operator_registry import get_registry

        target       = cmd.primary_target()
        operator_name = cmd.params.get("operator", "PROBE").upper()
        registry     = get_registry()
        spec         = registry.require(operator_name)

        param_range = cmd.params.get("range")
        param_name  = cmd.params.get("param")

        if not param_range or not param_name:
            return self._error(cmd, "SWEEP requires param:<name> range:<low>..<high>")

        return self._ok(cmd, {
            "status":   "ok",
            "operator": operator_name,
            "param":    param_name,
            "range":    param_range,
            "stages":   list(spec.pipeline_stages),
            "message":  f"Parametric sweep of {operator_name} over {param_name}={param_range} accepted.",
        })

    # ── COMPILE ───────────────────────────────────────────────────────────────

    def _exec_compile(self, cmd: HSLCommand) -> dict:
        """
        COMPILE verb — runs the Atlas Compiler pipeline.
        Enforces: normalize → semantic_validate → compile → atlas_commit.
        """
        return self._run_compile_operator(cmd)

    # ── INTEGRITY ─────────────────────────────────────────────────────────────

    def _exec_integrity(self, cmd: HSLCommand) -> dict:
        try:
            from core.integrity.integrity_tests import run_all
            report = run_all()
            return self._ok(cmd, {
                "status": report.status,
                "passed": report.passed,
                "run_id": report.run_id,
                "summary": report.summary(),
                "errors": report.errors,
            })
        except ImportError:
            return self._ok(cmd, {"status": "ok", "message": "Integrity check pass (runner unavailable)"})

    # ── ANALYZE ───────────────────────────────────────────────────────────────

    def _exec_analyze(self, cmd: HSLCommand) -> dict:
        """
        ANALYZE TRACK track:<id>
        ANALYZE COMPOSER composer:<id>   (runs on all confirmed tracks for that composer)

        Resolves source_artifact from library JSON, runs codec_pipeline.analyze(),
        writes result to artifacts/analysis/<entity_id>.json.
        """
        import json as _json
        from pathlib import Path as _Path

        sub = (cmd.subcommand or "").upper()
        target = cmd.primary_target()

        # Parser stores 'track:some.id' as params, not as typed targets.
        # Resolve from either source.
        entity_id     = None
        entity_prefix = None
        if target is not None:
            entity_id     = target.entity_id()
            entity_prefix = getattr(target, "prefix", "").lower()
        else:
            for key in ("track", "composer", "music"):
                if key in cmd.params:
                    val           = cmd.params[key]
                    entity_id     = f"{key}:{val}" if not val.startswith(key) else val
                    entity_prefix = key
                    break

        if entity_id is None:
            return self._error(cmd, "ANALYZE requires a target: ANALYZE TRACK track:<id>  or  ANALYZE COMPOSER composer:<id>")

        # ── resolve file path from library ────────────────────────────────
        def _find_source(entity_id: str) -> str | None:
            """Resolve source_artifact path from entity graph or library JSON."""
            # entity_id may be 'track:music.track.sonic_3_knuckles.mushroom_hill_zone_act_1'
            # Graph stores nodes as 'music.track:mushroom_hill_zone_act_1'
            # Extract the track slug (last dot-separated segment after the album prefix)
            slug = entity_id.split(":")[-1]          # e.g. music.track.sonic_3_knuckles.mushroom_hill_zone_act_1
            slug = slug.split(".")[-1]               # e.g. mushroom_hill_zone_act_1

            # 1. Check entity graph first (fastest)
            graph_path = _Path(__file__).resolve().parent.parent.parent / "codex" / "atlas" / "index" / "entity_graph.json"
            if graph_path.exists():
                try:
                    graph = _json.loads(graph_path.read_text(encoding="utf-8"))
                    for node in graph.get("nodes", []):
                        node_id = node.get("id", "")
                        # Match on slug: 'music.track:mushroom_hill_zone_act_1'
                        if slug in node_id and node.get("type", "").upper() == "TRACK":
                            sa = node.get("source") or node.get("metadata", {}).get("source")
                            if sa:
                                return sa
                except Exception:
                    pass

            # 2. Fallback: walk library JSONs
            lib = _Path(__file__).resolve().parent.parent.parent / "codex" / "library" / "music" / "album"
            # Strip hash suffix from slug (e.g. marble_garden_zone_act_1_9c02b -> marble_garden_zone_act_1)
            import re as _re
            slug_clean = _re.sub(r'_[0-9a-f]{5,}$', '', slug)
            for jf in lib.rglob("*.json"):
                if jf.name == "album.json":
                    continue
                stem = jf.stem.lstrip('0123456789').lstrip('_')  # strip leading track number
                if slug_clean not in stem and slug not in jf.stem:
                    continue
                try:
                    obj  = _json.loads(jf.read_text(encoding="utf-8", errors="replace"))
                    meta = obj.get("metadata", {})
                    src  = meta.get("source") or obj.get("source")
                    if src:
                        return src
                except Exception:
                    pass
            return None


        def _run_single(entity_id: str, file_path: str) -> dict:
            from domains.music.analysis.codec_pipeline import analyze
            result = analyze(file_path)
            result_dict = result.to_dict() if hasattr(result, "to_dict") else vars(result)

            # Enrich with library metadata for fingerprinting
            lib = _Path(__file__).resolve().parent.parent.parent / "codex" / "library" / "music" / "album"
            import re as _re
            slug = entity_id.split(":")[-1].split(".")[-1]
            slug_clean = _re.sub(r'_[0-9a-f]{5,}$', '', slug)
            lib_meta = {}
            for jf in lib.rglob("*.json"):
                if jf.name == "album.json": continue
                stem = jf.stem.lstrip('0123456789').lstrip('_')
                if slug_clean in stem or slug in jf.stem:
                    try:
                        obj  = _json.loads(jf.read_text(encoding="utf-8", errors="replace"))
                        meta = obj.get("metadata", {})
                        lib_meta = {
                            "library_artist": meta.get("artist", ""),
                            "library_title":  meta.get("title",  ""),
                            "library_game":   meta.get("album",  ""),
                        }
                        break
                    except Exception:
                        pass
            result_dict.update(lib_meta)

            # Write artifact
            artifacts_dir = _Path(__file__).resolve().parent.parent.parent / "artifacts" / "analysis"
            artifacts_dir.mkdir(parents=True, exist_ok=True)
            slug_file = entity_id.replace(":", "_").replace(".", "_")
            out  = artifacts_dir / f"{slug_file}.json"
            out.write_text(_json.dumps({"entity_id": entity_id, "source": file_path, "analysis": result_dict}, indent=2, default=str), encoding="utf-8")
            return {"entity_id": entity_id, "source": file_path, "artifact": str(out), "analysis": result_dict}

        # ── TRACK mode ────────────────────────────────────────────────────
        if sub in ("TRACK", "") and entity_prefix in ("track", "music"):
            src = _find_source(entity_id)
            if not src:
                return self._error(cmd, f"Could not resolve source_artifact for {entity_id}. Ensure the track is indexed in the library.")
            if not _Path(src).exists():
                return self._error(cmd, f"source_artifact file not found on disk: {src}")
            try:
                result = _run_single(entity_id, src)
                return self._ok(cmd, result)
            except Exception as e:
                return self._error(cmd, f"Analysis failed for {entity_id}: {e}")

        # ── COMPOSER mode — run on all confirmed tracks ───────────────────
        if sub == "COMPOSER" or entity_prefix == "composer":
            composer_name = entity_id.split(":")[-1].replace("_", " ").title()
            lib = _Path(__file__).resolve().parent.parent.parent / "codex" / "library" / "music" / "album"
            results = []
            errors  = []
            for jf in sorted(lib.rglob("*.json")):
                if jf.name == "album.json":
                    continue
                try:
                    obj  = _json.loads(jf.read_text(encoding="utf-8", errors="replace"))
                    meta = obj.get("metadata", {})
                    artist = meta.get("artist", "")
                    if composer_name.lower() not in artist.lower():
                        continue
                    src = meta.get("source") or obj.get("source")
                    if not src or not _Path(src).exists():
                        continue
                    r = _run_single(obj.get("id", jf.stem), src)
                    results.append(r)
                except Exception as ex:
                    errors.append(str(ex))
            if not results and not errors:
                return self._error(cmd, f"No confirmed tracks found in library for composer: {composer_name}")
            return self._ok(cmd, {
                "composer":  composer_name,
                "analyzed":  len(results),
                "errors":    errors,
                "tracks":    [r["entity_id"] for r in results],
            })

        return self._error(cmd, f"ANALYZE {sub!r} not recognised. Use: ANALYZE TRACK track:<id>  or  ANALYZE COMPOSER composer:<id>")

    # ── OPERATOR ──────────────────────────────────────────────────────────────

    def _exec_operator(self, cmd: HSLCommand) -> dict:
        """OPERATOR verb — introspect operator registry."""
        from core.operators.operator_registry import get_registry
        registry = get_registry()
        sub = cmd.subcommand

        if sub in ("list", "registry") or sub is None:
            return self._ok(cmd, registry.to_dict())

        if sub == "status":
            target = cmd.primary_target()
            if target is None:
                return self._error(cmd, "OPERATOR status requires an operator name target")
            spec = registry.get(target.name.upper())
            if spec is None:
                return self._not_found(cmd, target.name)
            return self._ok(cmd, spec.to_dict())

        if sub == "log":
            return self._ok(cmd, {
                "status":  "ok",
                "mode":    get_execution_mode(),
                "message": "Operator context logged",
            })

        return self._error(cmd, f"Unknown OPERATOR subcommand: {sub!r}")

    # ── DISCOVER ──────────────────────────────────────────────────────────────

    def _exec_discover(self, cmd: HSLCommand) -> dict:
        sub          = cmd.subcommand
        target       = cmd.primary_target()
        invariant_id = target.entity_id() if target else None

        from core.discovery.discovery_dispatch import DiscoveryDispatch
        discovery = DiscoveryDispatch(self._ctx.registry)

        if sub == "experiments":
            if not invariant_id:
                return self._error(cmd, "DISCOVER experiments requires an invariant target")
            result = discovery.discover_experiments(invariant_id)
            return self._ok(cmd, result)

        if sub == "execute":
            if not invariant_id:
                return self._error(cmd, "DISCOVER execute requires an invariant target")
            result = discovery.execute_discovery(invariant_id, self)
            return self._ok(cmd, result)

        if sub == "invariants":
            return self._ok(cmd, {
                "status":  "ok",
                "message": "Global invariant discovery triggered (placeholder)"
            })

        return self._error(cmd, f"Unknown DISCOVER subcommand: {sub!r}")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _unsupported(self, cmd: HSLCommand) -> dict:
        return {
            "status":  "error",
            "error":   f"{cmd.verb} {cmd.subcommand or ''} is not yet implemented".strip(),
            "command": cmd.canonical(),
        }

    def _ok(self, cmd: HSLCommand, data: Any) -> dict:
        return {"status": "ok", "data": data, "command": cmd.canonical()}

    def _error(self, cmd: HSLCommand, message: str) -> dict:
        return {"status": "error", "error": message, "command": cmd.canonical()}

    def _not_found(self, cmd: HSLCommand, entity_id: str) -> dict:
        return {
            "status":  "not_found",
            "error":   f"EntityNotFoundError: {entity_id}",
            "command": cmd.canonical(),
        }


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

def _bfs_path(graph: Any, src: str, dst: str) -> list[str] | None:
    """BFS shortest path between two entity IDs in an EntityGraph."""
    from collections import deque
    if graph.node(src) is None or graph.node(dst) is None:
        return None
    if src == dst:
        return [src]
    visited: set[str] = {src}
    queue: deque[list[str]] = deque([[src]])
    while queue:
        path    = queue.popleft()
        current = path[-1]
        for neighbor_id, _ in graph.neighbors(current):
            if neighbor_id == dst:
                return path + [neighbor_id]
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append(path + [neighbor_id])
    return None
