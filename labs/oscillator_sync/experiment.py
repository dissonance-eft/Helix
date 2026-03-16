import os
import json
import csv
import numpy as np
from core.python_suite.dynamics.kuramoto import KuramotoSystem
from core.python_suite.analysis.feature_extractor import FeatureExtractor

def run_experiment(n_oscillators=50, K=1.5, steps=500, dt=0.01):
    print(f"Running Oscillator Sync Experiment: N={n_oscillators}, K={K}")
    
    # 1. Initialize System
    system = KuramotoSystem(n_oscillators=n_oscillators, K=K)
    
    # 2. Simulate
    history = system.simulate(dt=dt, steps=steps)
    
    # 3. Calculate Synchronization Index over time
    sync_history = [system.order_parameter(theta)[0] for theta in history]
    
    # 4. Extract Features
    features = FeatureExtractor.extract_all({"sync_index": sync_history})
    features["convergence"] = FeatureExtractor.convergence_time(sync_history)
    
    # 5. Prepare Artifacts
    artifact_dir = f"artifacts/oscillator_sync_{int(np.random.rand()*1000)}"
    os.makedirs(artifact_dir, exist_ok=True)
    
    # Save parameters
    with open(os.path.join(artifact_dir, "parameters.json"), "w") as f:
        json.dump({"n": n_oscillators, "K": K, "steps": steps, "dt": dt}, f, indent=2)
        
    # Save results as CSV
    with open(os.path.join(artifact_dir, "results.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["step", "sync_index"])
        for i, val in enumerate(sync_history):
            writer.writerow([i, val])
            
    # Save metadata and features
    metadata = {
        "experiment": "oscillator_sync",
        "timestamp": "2026-03-15T22:00:00",
        "features": features,
        "final_sync": float(sync_history[-1])
    }
    with open(os.path.join(artifact_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
        
    print(f"Experiment complete. Artifact saved to {artifact_dir}")
    return artifact_dir

if __name__ == "__main__":
    run_experiment()
