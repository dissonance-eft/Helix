import json
import random
from pathlib import Path

def run_adversarial_sandbox(artifacts_dir: Path, domains_dir: Path = None):
    """
    Programmatic mutation of domain parameters to hunt for kernel-002 edge cases.
    Automatically generates theoretical counterexamples by altering structural assumptions.
    """
    print("--- Helix Adversarial Red-Teaming Sandbox ---")
    print("Hunting for Kernel-002 Edge Cases via Parameter Mutation...\n")
    
    if domains_dir is None:
        domains_dir = Path("data/domains")
        
    if not domains_dir.exists():
        print(f"Cannot find domains directory at {domains_dir}.")
        return
        
    domain_files = list(domains_dir.glob("*.json"))
    if not domain_files:
        print("No domain files found to mutate.")
        return
        
    print(f"Loaded {len(domain_files)} domains for adversarial mutation.")
    
    # 3 core mutation strategies to break the constraints
    mutations = [
        {"name": "Zero-Noise Limit", "target": "perturbation_operator", "inject": "Set explicit noise σ = 0"},
        {"name": "Infinite Dimensionality", "target": "dimensionality_form", "inject": "infinite (continuous spectrum)"},
        {"name": "Barrier Collapse", "target": "tau_relax", "inject": "tau_relax approaches 0 (instantaneous thermalization)"}
    ]
    
    # Select a random domain to red-team for this run
    target_path = random.choice(domain_files)
    
    try:
        with open(target_path, 'r', encoding='utf-8') as f:
            domain = json.load(f)
    except Exception as e:
        print(f"Error reading {target_path.name}: {e}")
        return
        
    print(f"\n[TARGET ACQUIRED]: {domain.get('id', target_path.name)}")
    print(f"Original Persistence Type: {domain.get('persistence_type', 'UNKNOWN')}\n")
    
    print("Executing Mutations:")
    failed = 0
    for idx, mut in enumerate(mutations):
        old_val = domain.get(mut['target'], 'UNDEFINED')
        print(f"  Mutation {idx+1}: {mut['name']}")
        print(f"    - Target Field: {mut['target']}")
        print(f"    - Old Value: {old_val}")
        print(f"    - New Value: {mut['inject']}")
        
        # Heuristic evaluator
        if mut['name'] == "Zero-Noise Limit" and domain.get('stability_condition', '').find('NOISE_CONSTRUCTIVE') != -1:
            print("    -> [RESULT]: COLLAPSE. This domain strictly requires noise to persist.")
            failed += 1
        elif mut['name'] == "Infinite Dimensionality" and domain.get('persistence_type') == "STATE":
            print("    -> [RESULT]: WARN. State persistence in infinite dimensions requires rigorous KAM bounds.")
        elif mut['name'] == "Barrier Collapse":
            print("    -> [RESULT]: COLLAPSE. Without relaxation delay, domain instantly tracks perturbation.")
            failed += 1
        else:
            print("    -> [RESULT]: STABLE. Mutation did not crack structural integrity.")
            
    print(f"\nRed-Team Summary: {failed}/{len(mutations)} mutations successfully broke the target domain's persistence.")
    if failed > 0:
        print("Recommendation: Check if these mutated conditions represent physically possible configurations.")
