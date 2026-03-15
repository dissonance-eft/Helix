"""
Falsification Analyzer — 04_labs/research/falsification_analyzer.py

Analyzes adversarial sweeps to test the Identity Hypothesis (H1) 
vs Coupeld Transition (H2) vs Shared Order (H3).
"""

import json
import os
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'helix.py').exists())

def analyze_falsification(exp_name: str):
    summary_path = ROOT / "07_artifacts" / "experiments" / exp_name / "summary.json"
    if not summary_path.exists():
        return {"error": "Summary not found"}

    with open(summary_path, 'r') as f:
        data = json.load(f)

    results = data.get("results_summary", [])
    
    # Track configurations specifically looking for divergence
    divergence_regimes = []
    h1_identity_score = 1.0
    
    # Dictionary to correlate probe pairs on the same exact parameter set
    # Using a hash of the parameters as key
    param_map = {}
    
    for r in results:
        param_hash = json.dumps(r['params'], sort_keys=True)
        probe = r['probe']
        passed = float(r['passed']) # 1.0 or 0.0
        
        if param_hash not in param_map:
            param_map[param_hash] = {}
        param_map[param_hash][probe] = passed

    # Check for divergence (Major Falsification of H1)
    divergences = 0
    total_comparisons = 0
    
    divergence_list = []
    
    for p_hash, probes in param_map.items():
        if "decision_compression" in probes and "oscillator_locking" in probes:
            total_comparisons += 1
            d_passed = probes["decision_compression"]
            o_passed = probes["oscillator_locking"]
            
            if d_passed != o_passed:
                divergences += 1
                divergence_list.append({
                    "params": json.loads(p_hash),
                    "decision": d_passed,
                    "oscillator": o_passed
                })

    diversion_rate = divergences / total_comparisons if total_comparisons > 0 else 0
    
    # Interpretation Logic
    verdict = "H1: Identity Hypothesis"
    if diversion_rate > 0.05:
        verdict = "H2: Coupled Transition Hypothesis (Falsified H1)"
    if diversion_rate > 0.5:
        verdict = "H3: Shared Order Parameter (Divergent Signals Observed)"

    report = {
        "experiment": exp_name,
        "total_comparisons": total_comparisons,
        "divergent_runs": divergences,
        "divergence_rate": diversion_rate,
        "verdict": verdict,
        "top_falsifiers": divergence_list[:10], # Top 10 divergence regimes
        "interpretation": {
            "H1_status": "REJECTED" if diversion_rate > 0.05 else "RETAINED",
            "critical_falsifier_topology": [d['params'].get('topology') for d in divergence_list if d['decision'] > d['oscillator']]
        }
    }

    out_path = ROOT / "06_atlas" / "decision_vs_sync_falsification.json"
    with open(out_path, 'w') as f:
        json.dump(report, f, indent=4)
    
    return report

if __name__ == "__main__":
    rep = analyze_falsification("adversarial_falsification_sweep")
    print(f"VERDICT: {rep.get('verdict')}")
    print(f"Divergence Rate: {rep.get('divergence_rate')}")
