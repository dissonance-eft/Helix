import json
import os
import sys
from pathlib import Path

# Helix Ring Architecture Imports
ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from core.bases import BASES
from core.eip import EpistemicIrreversibility
from core.collapse import CollapseLogic

def run_oracle(domain_path):
    with open(domain_path, 'r', encoding='utf-8') as f:
        domain = json.load(f)
    
    print(f"\n--- HELIX STRUCTURAL ORACLE: {domain['id'].upper()} ---")
    print(f"Domain: {domain['domain']}")
    print(f"B3 Mapping: {domain['notes']}")
    
    # Audit for Epistemic Irreversibility (Ring 0)
    is_irreversible = EpistemicIrreversibility.is_irreversible(
        domain['failure_mode'], 
        domain.get('stability_condition', 'unknown')
    )
    commitment = EpistemicIrreversibility.classify_commitment(is_irreversible)
    
    print(f"Status: {commitment}")
    
    # Classify Outcomes (Ring 0)
    # Mapping 'timescale_regime' to stability metrics (Simulation)
    forecast = CollapseLogic.classify_stability(
        {'B1': 0.005 if "COLLAPSE" in domain['failure_mode'] else 1.0},
        {'SF1': "ATTACHABLE"}
    )
    
    print(f"Forecast: {forecast}")
    
    if is_irreversible:
        print("\n[ALERT] EIP_VIOLATION: The collapse of this system involves the loss of its referential symbols (Ring 0: B4). Recovery of state-space history is computationally impossible.")
    
    print("-" * 50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Default to the coolest domain
        target = ROOT / 'sandbox' / 'domain_data' / 'domains' / 'bizarre_bronze_age_collapse.json'
    else:
        target = Path(sys.argv[1])
        
    run_oracle(target)
