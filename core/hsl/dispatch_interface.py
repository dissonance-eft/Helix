"""
HSL Dispatch Interface
======================
Routes a validated HSLCommand AST to the kernel dispatcher.

Lifecycle:
  - Parser:   raw string   -> HSLCommand AST
  - Validator: HSLCommand  -> validated HSLCommand (or error)
  - Logger:   HSLCommand   -> artifact record
  - Dispatch: HSLCommand   -> dispatcher envelope -> engine.run()

No execution logic belongs here.
No dispatch logic belongs in the parser or validator.
"""
from __future__ import annotations

from core.hsl.parser import parse
from core.hsl.validator import validate
from core.hsl.errors import HSLError


def dispatch(raw_command: str, dispatcher=None, log: bool = True) -> dict:
    """
    Full HSL pipeline: parse -> validate -> log -> dispatch.

    If dispatcher is None, returns validated AST info without executing.
    """
    from core.hsl.command_logger import CommandLogger

    try:
        cmd = parse(raw_command)
        cmd = validate(cmd)
    except HSLError as e:
        return {"status": "hsl_error", "error": e.to_dict()}

    if log:
        CommandLogger.log(cmd)

    if dispatcher is None:
        return {
            "status":    "validated",
            "canonical": cmd.canonical(),
            "ast":       cmd.to_dict(),
        }

    # Build dispatcher envelope
    primary = cmd.primary_target()
    envelope = cmd.to_dict()
    envelope["target"]  = primary.name if primary else (cmd.subcommand or "")
    envelope["engine"]  = cmd.get_engine()

    return dispatcher.route(envelope)
