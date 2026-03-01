import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('c:/Users/dissonance/Desktop/Helix')
DOMAINS_DIR = ROOT / 'domains'

domains = []
for p in DOMAINS_DIR.glob('*.json'):
    with open(p, 'r') as f:
        domains.append(json.load(f))

def get_entropy(labels):
    c = Counter(labels)
    t = len(labels)
    if t == 0: return 0.0
    return -sum((v/t)*math.log2(v/t) for v in c.values() if v > 0)

# 1. Structural Voids and Locked Coordinates
# Are there (S1c, Ontology) pairs that strictly enforce ONE boundary type with 0 entropy?
cells = defaultdict(list)
for d in domains:
    s = d.get('substrate_S1c', 'UNKNOWN')
    o = d.get('persistence_ontology', 'UNKNOWN')
    b = d.get('boundary_type_primary', 'UNKNOWN')
    cells[(s, o)].append(b)

print("--- STRUCTURAL LOCKS & VOIDS (N_domains > 10) ---")
for (s, o), b_list in cells.items():
    if len(b_list) > 10:
        h = get_entropy(b_list)
        if h == 0.0:
            locked_type = b_list[0]
            print(f"LOCKED CELL: Substrate={s} + Ontology={o} -> STRICTLY {locked_type} (n={len(b_list)}, H=0.0)")

print("\n--- MEASUREMENT LAYER ANOMALIES ---")
# Let's see if the sign of 'phi' strictly correlates with 'collapse' vs 'divergence'
sign_b_types = defaultdict(list)
for d in domains:
    if "thresholds" in d and len(d["thresholds"]) > 0:
        phi = d["thresholds"][0].get('phi', 0)
        b = d.get('boundary_type_primary', 'UNKNOWN')
        sign = "POSITIVE_PHI" if phi > 0 else "NEGATIVE_PHI"
        sign_b_types[b].append(sign)

for b, signs in sign_b_types.items():
    if len(signs) > 5:
        c = Counter(signs)
        maj_ratio = c.most_common(1)[0][1] / len(signs)
        if maj_ratio > 0.8:
            print(f"DIRECTIONAL BIAS: {b} is {maj_ratio*100:.1f}% {c.most_common(1)[0][0]} relative to threshold.")

print("\n--- HYBRID DECOUPLING SIGNATURES ---")
# In Hybrid systems, do they fail differently based on their Persistence Ontology?
hybrid_bs = defaultdict(list)
for d in domains:
    s = d.get('substrate_S1c', 'UNKNOWN')
    if s == 'HYBRID':
        o = d.get('persistence_ontology', 'UNKNOWN')
        b = d.get('boundary_type_primary', 'UNKNOWN')
        hybrid_bs[o].append(b)

for o, b_list in hybrid_bs.items():
    if len(b_list) > 5:
        top = Counter(b_list).most_common(2)
        print(f"HYBRID with {o} -> {top}")
