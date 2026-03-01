import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path('c:/Users/dissonance/Desktop/Helix')
DOMAINS_DIR = ROOT / 'domains'

domains = []
for p in DOMAINS_DIR.glob('*.json'):
    with open(p, 'r') as f:
        domains.append(json.load(f))

# 1. TIMESCALE VS LOCALITY
print("--- TIMESCALE (T1) VS BREAKDOWN LOCALITY ---")
t1_loc = defaultdict(list)
for d in domains:
    t1 = d.get('T1', 'UNKNOWN')
    loc = d.get('boundary_locality', 'UNKNOWN')
    t1_loc[t1].append(loc)

for t1, locs in t1_loc.items():
    if t1 != 'UNKNOWN':
        c = Counter(locs)
        total = len(locs)
        print(f"{t1}: {c['GLOBAL']/total*100:.1f}% GLOBAL, {c['LOCAL']/total*100:.1f}% LOCAL (n={total})")

# 2. LOCALITY VS DIMENSIONALITY CHANGE
print("\n--- LOCALITY VS DIMENSIONALITY COLLAPSE ---")
loc_dim = defaultdict(list)
for d in domains:
    loc = d.get('boundary_locality', 'UNKNOWN')
    dim = d.get('boundary_dimensionality_change', 'UNKNOWN')
    loc_dim[loc].append(dim)

for loc, dims in loc_dim.items():
    if loc != 'UNKNOWN':
        c = Counter(dims)
        total = len(dims)
        print(f"When failure is {loc}: {c['YES']/total*100:.1f}% involve dimensionality change (n={total})")

# 3. FAST PERTURBATION VULNERABILITY (Which substrates break when hit fast?)
print("\n--- WHICH SUBSTRATES SURVIVE FAST PERTURBATIONS? ---")
fast_subs = defaultdict(list)
for d in domains:
    if d.get('T1') == 'T1_FAST_PERTURB':
        s = d.get('substrate_S1c', 'UNKNOWN')
        b = d.get('boundary_type_primary', 'UNKNOWN')
        fast_subs[s].append(b)

for s, bs in sorted(fast_subs.items(), key=lambda x: len(x[1]), reverse=True):
    c = Counter(bs)
    top = c.most_common(1)[0]
    print(f"{s} hit with FAST perturbation -> {top[0]} ({top[1]}/{len(bs)} cases)")
