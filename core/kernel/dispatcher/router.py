# Kernel Dispatcher Router — Phase 9
# Resolves engine from HIL envelope and delegates execution.
# Runs integrity gate before any experiment dispatch.

from __future__ import annotations

_INTEGRITY_CHECKED = False   # process-level gate: only check once per session


def _run_integrity_gate(verbose: bool = False) -> bool:
    """Run the Phase 9 integrity gate. Returns True if safe to proceed."""
    global _INTEGRITY_CHECKED
    if _INTEGRITY_CHECKED:
        return True
    try:
        from core.integrity.integrity_tests import gate
        ok = gate(verbose=verbose)
    except ImportError:
        # Integrity module not yet available — allow dispatch but warn
        print("[dispatcher] WARNING: core.integrity not found — skipping integrity gate")
        ok = True
    _INTEGRITY_CHECKED = True
    return ok


try:
    from engines.python.engine import PythonEngine
    _python_engine = PythonEngine()
except ImportError:
    _python_engine = None  # type: ignore

# from engines.godot.adapter import GodotAdapter  # Phase 10

ENGINE_REGISTRY: dict = {
    "python": _python_engine,
    # "godot": GodotAdapter(),
}


class Dispatcher:
    """
    Routes normalized HIL envelopes to the correct engine.

    Phase 9 pipeline:
      HIL envelope -> integrity gate -> engine dispatch -> result
    """

    def __init__(self, skip_integrity: bool = False):
        self._skip_integrity = skip_integrity

    def route(self, envelope: dict) -> dict:
        # ── Phase 9: integrity gate ──────────────────────────────────────
        if not self._skip_integrity:
            ok = _run_integrity_gate(verbose=False)
            if not ok:
                return {
                    "status":  "INVALID_ENVIRONMENT",
                    "message": "Integrity gate failed — experiment halted. "
                               "Run core/integrity/integrity_tests.py for details.",
                    "artifact_flag": "INVALID_ENVIRONMENT",
                }

        # ── Engine dispatch ──────────────────────────────────────────────
        target     = envelope.get("target", "")
        engine_key = target.split(".")[0] if "." in target else "python"

        engine = ENGINE_REGISTRY.get(engine_key)
        if engine is None:
            return {
                "status":  "error",
                "message": f"No engine registered for '{engine_key}'",
            }

        return engine.run(envelope)
