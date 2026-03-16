# Python Engine — Helix execution substrate for computational experiments.
# This is the primary engine for non-spatial, mathematical experiments.

import importlib
import os


PROBE_REGISTRY = {
    "network":       "probes.network",
    "dynamical":     "probes.dynamical",
    "oscillator":    "probes.oscillator",
    "cellular":      "probes.cellular",
    "evolutionary":  "probes.evolutionary",
    "information":   "probes.information",
    "dataset":       "probes.dataset",
}


class PythonEngine:
    """
    Helix Python execution engine.
    Receives normalized HIL envelopes and routes them to probe modules.
    """

    name = "python"

    def run(self, envelope: dict) -> dict:
        target = envelope.get("target", "")
        params = envelope.get("params", {})

        probe_key = target.split(".")[-1] if "." in target else target
        
        # Simple fuzzy matching for common probe names
        matched_key = None
        if probe_key in PROBE_REGISTRY:
            matched_key = probe_key
        else:
            for k in PROBE_REGISTRY:
                if k in probe_key:
                    matched_key = k
                    break

        if not matched_key:
            return {"status": "error", "message": f"Unknown probe '{probe_key}'"}

        try:
            module_path = PROBE_REGISTRY[matched_key]
            module = importlib.import_module(f"engines.python.{module_path}")
            result = module.run(params)
            return {"status": "ok", "result": result}
        except ImportError as e:
            return {"status": "not_implemented", "message": str(e)}
        except Exception as e:
            return {"status": "error", "message": str(e)}
