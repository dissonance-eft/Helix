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

print("=== DEEP QUERY 5: STRUCTURAL BLINDNESS (METRIC VS DIMENSIONALITY) ===")
# Do we use continuous "metrics" to track discontinuous "state spaces"?
# If so, do they correlate with unexpected failures?
blind_spots = defaultdict(list)
for d in domains:
    dim = d.get('dimensionality_form', 'UNKNOWN')
    
    # Check what kind of metric is tracking it
    metrics = d.get('observable_metrics', [])
    m_types = []
    for m in metrics:
        if isinstance(m, dict):
            m_types.append(m.get('type', 'CUSTOM'))
        elif isinstance(m, str):
            m_types.append('CUSTOM')
            
    b = d.get('boundary_type_primary', 'UNKNOWN')
    t1 = d.get('T1', 'UNKNOWN')
    
    for m_t in m_types:
        blind_spots[(dim, m_t)].append(b)

print("How does State Dimensionality interact with Observability?")
for (dim, m_t), bs in sorted(blind_spots.items(), key=lambda x: len(x[1]), reverse=True):
    if len(bs) >= 10:
        c = Counter(bs)
        top = c.most_common(1)[0]
        acc = top[1]/len(bs)
        if acc > 0.5:
            print(f"When tracking a [{dim}] space with [{m_t}] -> {acc*100:.0f}% fail via {top[0]} (n={len(bs)})")

print("\n=== DEEP QUERY 6: THE 'EDGE CONDITION' CASCADE ===")
# Is there a correlation between the system's "edge conditions" and its final failure mode?
# In cybernetics, edge cases are where the mapping function diverges.
edge_words = defaultdict(list)
for d in domains:
    edges = d.get('edge_conditions', [])
    b = d.get('boundary_type_primary', 'UNKNOWN')
    for e in edges:
        e = e.lower()
        if 'limit' in e: edge_words['limit'].append(b)
        elif 'noise' in e: edge_words['noise'].append(b)
        elif 'latency' in e: edge_words['latency'].append(b)
        elif 'scale' in e: edge_words['scale'].append(b)
        elif 'rate' in e: edge_words['rate'].append(b)

for w, bs in edge_words.items():
    if len(bs) >= 2:
        top = Counter(bs).most_common(2)
        print(f"When Edge Condition involves [{w.upper()}]: Fails via {top}")

