import importlib
import os

class PythonExperimentLoader:
    """
    Loads Python experiment probes.
    """
    PROBE_REGISTRY = {
        "network":       "probes.network",
        "dynamical":     "probes.dynamical",
        "oscillator":    "probes.oscillator",
        "cellular":      "probes.cellular",
        "evolutionary":  "probes.evolutionary",
        "information":   "probes.information",
        "dataset":       "probes.dataset",
    }

    @staticmethod
    def load(experiment_name: str):
        # Fuzzy matching as implemented in Phase 12
        probe_key = experiment_name.split(".")[-1] if "." in experiment_name else experiment_name
        
        matched_key = None
        if probe_key in PythonExperimentLoader.PROBE_REGISTRY:
            matched_key = probe_key
        else:
            for k in PythonExperimentLoader.PROBE_REGISTRY:
                if k in probe_key:
                    matched_key = k
                    break

        if not matched_key:
            return None

        module_path = PythonExperimentLoader.PROBE_REGISTRY[matched_key]
        try:
            return importlib.import_module(f"engines.python.{module_path}")
        except ImportError:
            return None
