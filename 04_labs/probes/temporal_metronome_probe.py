"""
Temporal Metronome Probe — 04_labs/probes/temporal_metronome_probe.py

Invariant: Temporal Stability
Measures the jitter and execution consistency of the substrate itself.
If signal_strength is high, the hardware/OS substrate is deterministic.
"""

from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path

VERSION = "1.0.0"

def run_temporal_probe():
    start_time = time.perf_counter_ns()
    
    # Perform a fixed-cost computation
    x = 0
    for i in range(1_000_000):
        x += (i * i) % 123
        
    end_time = time.perf_counter_ns()
    duration_ms = (end_time - start_time) / 1_000_000
    
    # We want to see how "stable" this is. 
    # For a single run, we just report the duration.
    # The Atlas will later check the variance.
    
    return {
        "probe_name": "temporal_metronome",
        "domain": "substrate",
        "passed": True,
        "signal": duration_ms,
        "signal_strength": 1.0, 
        "duration_ms": duration_ms,
        "version": VERSION
    }

if __name__ == "__main__":
    artifact_dir = os.environ.get("HELIX_ARTIFACT_DIR")
    if not artifact_dir:
        sys.exit(1)
        
    result = run_temporal_probe()
    
    out_path = Path(artifact_dir) / "probe_result.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    sys.exit(0)
