import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('c:/Users/dissonance/Desktop/Helix')
DOMAINS_DIR = ROOT / 'domains'

domains = []
for p in DOMAINS_DIR.glob('*.json'):
    with open(p, 'r') as f:
        domains.append(json.load(f))

print("=== DEEP QUERY 1: THE DIMENSIONALITY CONSERVATION LAW ===")
# Which substrates actually lose their dimensions when they break?
sub_dim = defaultdict(list)
for d in domains:
    s = d.get('substrate_S1c', 'UNKNOWN')
    dim = d.get('boundary_dimensionality_change', 'UNKNOWN')
    sub_dim[s].append(dim)

for s, dims in sub_dim.items():
    if s != 'UNKNOWN':
        c = Counter(dims)
        total = len(dims)
        yes_pct = c.get('YES', 0) / total * 100
        print(f"Substrate [{s}]: {yes_pct:.1f}% of collapses destroy the mathematical dimensions (n={total})")

print("\n=== DEEP QUERY 2: TIME-SCALED ONTOLOGY SHATTERING ===")
# How does the speed of stress (T1) interact with the goal of the system (Ontology)?
t1_ont_b = defaultdict(list)
for d in domains:
    t1 = d.get('T1', 'UNKNOWN')
    ont = d.get('persistence_ontology', 'UNKNOWN')
    b = d.get('boundary_type_primary', 'UNKNOWN')
    if t1 != 'UNKNOWN' and ont != 'UNKNOWN':
        t1_ont_b[(t1, ont)].append(b)

for (t1, ont), bs in sorted(t1_ont_b.items(), key=lambda x: (x[0][0], len(x[1])), reverse=True):
    if len(bs) >= 5: # Only significant clusters
        top = Counter(bs).most_common(1)[0]
        acc = top[1]/len(bs)
        if acc > 0.7: # Highly deterministic shattering
            print(f"Goal [{ont}] hit {t1.replace('T1_','')} -> {acc*100:.0f}% lock into {top[0]} (n={len(bs)})")

print("\n=== DEEP QUERY 3: MAINTENANCE NOISE VULNERABILITY ===")
# Which combinations are vulnerable to "Maintenance-Noise Aliasing" 
# (where the system's own feedback/correction operators cause the collapse)
mna_targets = []
for d in domains:
    t = d.get('failure_reason_target', '')
    if t == 'MAINTENANCE_NOISE_ALIASING':
        s = d.get('substrate_S1c', 'UNKNOWN')
        ont = d.get('persistence_ontology', 'UNKNOWN')
        mna_targets.append(f"{s} + {ont}")

if mna_targets:
    c = Counter(mna_targets)
    for pair, count in c.most_common(3):
        print(f"Top MNA Vulnerability: {pair} (n={count})")
else:
    print("No domains explicitly tagged with MNA vulnerability in current subset.")

print("\n=== DEEP QUERY 4: THE HYBRID 'GHOST' METRIC ===")
# In eligible numeric combinations, do HYBRID domains have a distinctly different distance 
# to collapse (phi) than pure physics models when they break?
hybrid_phi = []
pure_phi = []
for d in domains:
    m = d.get('metric_layer', {})
    if m.get('eligible') and m.get('metric_phi') is not None:
        phi = abs(m.get('metric_phi'))
        if d.get('substrate_S1c') == 'HYBRID':
            hybrid_phi.append(phi)
        else:
            pure_phi.append(phi)

if hybrid_phi and pure_phi:
    h_mean = sum(hybrid_phi)/len(hybrid_phi)
    p_mean = sum(pure_phi)/len(pure_phi)
    print(f"Average absolute distance boundary for PURE geometry: {p_mean:.4f}")
    print(f"Average absolute distance boundary for HYBRID geometry: {h_mean:.4f}")
    if h_mean < p_mean:
         print("-> HYBRID domains mathematically collapse significantly CLOSER to their intended setpoints than pure geometrical ones (brittleness).")
    else:
         print("-> HYBRID domains exhibit higher tolerance bounds than expected.")
else:
    print("Not enough numeric proxies to analyze Hybrid phi variance.")
