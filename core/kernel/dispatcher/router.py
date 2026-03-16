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




from core.runner.experiment_runner import ExperimentRunner
from core.runner.sweep_runner import SweepRunner
from core.runner.scheduler import Scheduler

from core.kernel.engine_registry import EngineRegistry

class Dispatcher:
    """
    Routes normalized HIL envelopes to the correct engine through the Orchestrator.

    Phase 13 pipeline:
      HIL envelope -> integrity gate -> scheduler -> experiment runner -> engine -> result
    """

    def __init__(self, skip_integrity: bool = False):
        self._skip_integrity = skip_integrity
        self.experiment_runner = ExperimentRunner()
        self.sweep_runner = SweepRunner(self.experiment_runner)
        self.scheduler = Scheduler(self.experiment_runner, self.sweep_runner)

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

        # ── Orchestrator dispatch ────────────────────────────────────────
        return self.scheduler.dispatch(envelope)
