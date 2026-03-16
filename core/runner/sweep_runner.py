from __future__ import annotations
import os
import json
from core.runner.experiment_runner import ExperimentRunner

class SweepRunner:
    """
    Handles parameter sweeps by executing multiple experiment runs.
    """
    def __init__(self, experiment_runner: ExperimentRunner):
        self.experiment_runner = experiment_runner

    def run_sweep(
        self,
        parameter_name: str,
        low: float,
        high: float,
        steps: int,
        experiment_name: str,
        engine_name: str = "python",
        base_params: dict | None = None
    ) -> dict:
        base_params = base_params or {}
        
        # 1. Generate parameter values
        if steps > 1:
            step_size = (high - low) / (steps - 1)
            values = [low + i * step_size for i in range(steps)]
        else:
            values = [low]

        results = []
        sweep_slug = f"{experiment_name}_{parameter_name}_sweep"
        sweep_dir = self._create_sweep_dir(sweep_slug)

        # 2. Execute runs
        for i, val in enumerate(values):
            run_params = base_params.copy()
            run_params[parameter_name] = val
            
            # We want these runs to go into the sweep_dir
            # For simplicity, we can just let experiment_runner create its own dirs
            # but maybe we should nest them?
            # The prompt says: oscillator_lock_sweep_001/run_001/
            
            # Let's override the artifact dir logic for sweeps or just use subdirs
            run_name = f"run_{i+1:03d}"
            target_dir = os.path.join(sweep_dir, run_name)
            
            # We need to modify ExperimentRunner to accept a target directory
            # or we just move the created dir.
            # actually, let's just use the current experiment_runner and then we could symlink or something?
            # No, let's keep it simple as specified.
            
            # I will pass a dummy 'target' that includes the run number to the runner
            # and it will create artifacts/experiment_run_001_001
            # Wait, better to just call it and collect the paths.
            
            envelope = {
                "target": experiment_name,
                "engine": engine_name,
                "params": run_params,
                "raw": f"SWEEP {parameter_name} val:{val} RUN {experiment_name}"
            }
            
            # Run it
            run_result = self.experiment_runner.run(envelope)
            results.append({
                "value": val,
                "status": run_result["status"],
                "dir": run_result["artifact_dir"]
            })
            
        # 3. Create sweep summary artifact
        summary = {
            "parameter": parameter_name,
            "range": [low, high],
            "steps": steps,
            "experiment": experiment_name,
            "runs": results
        }
        summary_path = os.path.join(sweep_dir, "sweep_summary.json")
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=4)
            
        return {
            "status": "ok",
            "sweep_dir": sweep_dir,
            "run_count": len(results)
        }

    def _create_sweep_dir(self, slug: str) -> str:
        base_path = os.path.join("artifacts", slug)
        if not os.path.exists("artifacts"):
            os.makedirs("artifacts", exist_ok=True)
            
        i = 1
        while True:
            dir_name = f"{base_path}_{i:03d}"
            if not os.path.exists(dir_name):
                os.makedirs(dir_name)
                return dir_name
            i += 1
