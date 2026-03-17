"""
HIL Interpreter — Helix SPEC-08
================================
Parse, validate, resolve entities, and execute HIL commands.

Entry point:
    run_command(raw: str, context: CommandContext | None = None) -> dict

Execution flow:
    run_command(raw)
      → parse(raw)                    # core/hil/parser.py
      → validate(cmd)                 # core/hil/validator.py
      → context = CommandContext.default() if not provided
      → HILInterpreter(context).execute(cmd)
      → return result dict

Result format:
    {"status": "ok",        "data": ..., "command": cmd.canonical()}
    {"status": "not_found", "error": "EntityNotFoundError: ...", "command": ...}
    {"status": "error",     "error": "...", "command": ...}
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from core.hil.ast_nodes import HILCommand
from core.hil.context import CommandContext
from core.hil.errors import HILError
from core.hil.parser import parse
from core.hil.validator import validate
from core.entities.resolver import EntityNotFoundError, EntityResolver


def run_command(raw: str, context: CommandContext | None = None) -> dict:
    """
    Parse, validate, resolve entities, and execute a HIL command.

    Returns a result dict with keys: status, data or error, command.
    Never raises — all errors are captured into the result dict.
    """
    try:
        cmd = parse(raw)
    except HILError as e:
        return {"status": "error", "error": str(e), "command": raw}
    except Exception as e:
        return {"status": "error", "error": f"ParseError: {e}", "command": raw}

    try:
        validate(cmd)
    except HILError as e:
        return {"status": "error", "error": str(e), "command": cmd.canonical()}
    except Exception as e:
        return {"status": "error", "error": f"ValidationError: {e}", "command": cmd.canonical()}

    if context is None:
        context = CommandContext.default()

    interp = HILInterpreter(context)
    return interp.execute(cmd)


class HILInterpreter:
    """
    Executes validated HIL commands against a CommandContext.
    """

    def __init__(self, context: CommandContext) -> None:
        self._ctx = context

    def execute(self, cmd: HILCommand) -> dict:
        dispatch = {
            "ENTITY":    self._exec_entity,
            "GRAPH":     self._exec_graph,
            "SUBSTRATE": self._exec_substrate,
            "ANALYZE":   self._exec_analyze,
        }
        handler = dispatch.get(cmd.verb)
        if handler is None:
            return self._unsupported(cmd)
        try:
            return handler(cmd)
        except EntityNotFoundError as e:
            return {"status": "not_found", "error": str(e), "command": cmd.canonical()}
        except Exception as e:
            return {"status": "error", "error": str(e), "command": cmd.canonical()}

    # ── ENTITY ────────────────────────────────────────────────────────────────

    def _exec_entity(self, cmd: HILCommand) -> dict:
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
            entities       = resolver.all()
            if type_filter:
                entities = [e for e in entities if e.type.lower() == type_filter.lower()]
            if ns_filter:
                entities = [e for e in entities if e.namespace == ns_filter.lower()]
            return self._ok(cmd, {"entities": [e.to_dict() for e in entities], "count": len(entities)})

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
            return self._ok(cmd, {"linked": target.entity_id(), "relation": relation.upper(), "to": target_id})

        if sub == "add":
            params  = cmd.params
            target  = cmd.primary_target()
            if target is None:
                return self._error(cmd, "ENTITY add requires a typed entity reference")
            entity_id = target.entity_id()
            name      = params.get("name", target.name)
            type_str  = params.get("type", target.prefix.capitalize())
            if self._ctx.registry is None:
                return self._error(cmd, "No registry in context")
            from core.entities.schema import Entity
            entity = Entity(
                id=entity_id,
                type=type_str,
                name=name,
                metadata={
                    "source": "hil",
                    "source_stage": "hil_add",
                    "source_artifact": "manual",
                    "extraction_method": "hil_command",
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

    def _exec_graph(self, cmd: HILCommand) -> dict:
        sub    = cmd.subcommand
        graph  = self._ctx.graph

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
            src = targets[0].entity_id()
            dst = targets[1].entity_id()
            # BFS over EntityGraph adjacency
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

    def _exec_substrate(self, cmd: HILCommand) -> dict:
        sub = cmd.subcommand
        substrates_root = Path(__file__).parent.parent.parent / "substrates"

        if sub == "list":
            dirs = [d.name for d in sorted(substrates_root.iterdir()) if d.is_dir() and not d.name.startswith("_")]
            return self._ok(cmd, {"substrates": dirs})

        if sub == "info":
            name = cmd.params.get("name") or (cmd.primary_target().name if cmd.primary_target() else None)
            if not name:
                return self._error(cmd, "SUBSTRATE info requires name:substrate_name")
            substrate_dir = substrates_root / name
            if not substrate_dir.exists():
                return self._not_found(cmd, f"substrate:{name}")
            files = [f.name for f in substrate_dir.iterdir() if f.is_file()]
            return self._ok(cmd, {"name": name, "path": str(substrate_dir), "files": files})

        if sub == "run":
            name = cmd.params.get("name") or (cmd.primary_target().name if cmd.primary_target() else None)
            if not name:
                return self._error(cmd, "SUBSTRATE run requires name:substrate_name")
            if name == "music":
                try:
                    from substrates.music.pipeline import MusicSubstratePipeline
                    # Parse optional stage list: stages:1,2,9
                    stages_param = cmd.params.get("stages")
                    stages = [int(s) for s in str(stages_param).split(",") if s.strip().isdigit()] if stages_param else None
                    # Parse optional soundtrack filter
                    soundtrack = cmd.params.get("soundtrack")
                    # Parse optional resume_from
                    resume_raw = cmd.params.get("resume")
                    resume_from = int(resume_raw) if resume_raw and str(resume_raw).isdigit() else 1
                    pipeline = MusicSubstratePipeline(
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

    # ── ANALYZE ───────────────────────────────────────────────────────────────

    def _exec_analyze(self, cmd: HILCommand) -> dict:
        return self._unsupported(cmd)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _unsupported(self, cmd: HILCommand) -> dict:
        return {
            "status":  "error",
            "error":   f"{cmd.verb} {cmd.subcommand or ''} is not yet implemented in the interpreter".strip(),
            "command": cmd.canonical(),
        }

    def _ok(self, cmd: HILCommand, data: Any) -> dict:
        return {"status": "ok", "data": data, "command": cmd.canonical()}

    def _error(self, cmd: HILCommand, message: str) -> dict:
        return {"status": "error", "error": message, "command": cmd.canonical()}

    def _not_found(self, cmd: HILCommand, entity_id: str) -> dict:
        return {
            "status":  "not_found",
            "error":   f"EntityNotFoundError: {entity_id}",
            "command": cmd.canonical(),
        }


# ── Module-level helpers ───────────────────────────────────────────────────────

def _bfs_path(graph: Any, src: str, dst: str) -> list[str] | None:
    """BFS shortest path between two entity IDs in an EntityGraph. Returns None if unreachable."""
    from collections import deque
    if graph.node(src) is None or graph.node(dst) is None:
        return None
    if src == dst:
        return [src]
    visited: set[str] = {src}
    queue: deque[list[str]] = deque([[src]])
    while queue:
        path = queue.popleft()
        current = path[-1]
        for neighbor_id, _ in graph.neighbors(current):
            if neighbor_id == dst:
                return path + [neighbor_id]
            if neighbor_id not in visited:
                visited.add(neighbor_id)
                queue.append(path + [neighbor_id])
    return None
