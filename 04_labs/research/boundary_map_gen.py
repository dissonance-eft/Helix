import json
from pathlib import Path
from collections import defaultdict

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'helix.py').exists())

def generate_boundary_map():
    summary_path = ROOT / "07_artifacts" / "experiments" / "compression_boundary_scan" / "summary.json"
    with open(summary_path, 'r') as f:
        data = json.load(f)
        
    results = data.get("results_summary", [])
    
    # Heatmap: map (agent_count, competition_strength) -> signal strength / pass rate
    # But wait, signal strength isn't saved in the summary by the current runner, only "passed", "params".
    # Wait, the summary only saves "passed". So heatmap is just pass rate (0.0 to 1.0).
    heatmap = {}
    
    agent_threshold = None
    competition_threshold = None
    
    passed_agents = []
    passed_comp = []
    
    for r in results:
        params = r["params"]
        a_c = params["agent_count"]
        c_s = params["competition_strength"]
        key = f"agent_count={a_c}, competition_strength={c_s}"
        
        if key not in heatmap:
            heatmap[key] = {"total": 0, "passed": 0}
            
        heatmap[key]["total"] += 1
        if r["passed"]:
            heatmap[key]["passed"] += 1
            passed_agents.append(a_c)
            passed_comp.append(c_s)
            
    # Calculate pass rate
    final_heatmap = {}
    for k, v in heatmap.items():
        if v["total"] > 0:
            final_heatmap[k] = round(v["passed"] / v["total"], 4)
            
    if passed_agents:
        agent_threshold = min(passed_agents)
    if passed_comp:
        competition_threshold = min(passed_comp)
        
    output = {
        "agent_threshold_first_appearance": agent_threshold,
        "competition_threshold_first_appearance": competition_threshold,
        "signal_strength_heatmap_by_pass_rate": final_heatmap
    }
    
    out_path = ROOT / "07_artifacts" / "experiments" / "compression_boundary_scan" / "compression_boundary_map.json"
    with open(out_path, 'w') as f:
        json.dump(output, f, indent=4)
        
    print(f"Agent threshold: {agent_threshold}")
    print(f"Competition threshold: {competition_threshold}")
    print(f"Map saved to {out_path}")

if __name__ == '__main__':
    generate_boundary_map()
