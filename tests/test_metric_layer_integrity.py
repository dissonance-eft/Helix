import json
from pathlib import Path

ROOT = Path('c:/Users/dissonance/Desktop/Helix')
DOMAINS_DIR = ROOT / 'domains'

domains = [json.load(open(p)) for p in DOMAINS_DIR.glob('*.json')]

tests_passed = True
for d in domains:
    m = d.get('metric_layer')
    if not m:
        tests_passed = False
        print(f"Missing metric_layer in {d['id']}")
        
    if m['distance_value'] is not None:
        if len(m['provenance']['assumptions']) > 0 or m['provenance']['external_knowledge']:
            tests_passed = False
            print(f"Invalid provenance for numeric value in {d['id']}")
        if len(m['provenance']['used_fields']) == 0:
            tests_passed = False
            print(f"Missing used_fields for numeric value in {d['id']}")
            
    if not m['eligible'] and m['distance_value'] is not None:
        tests_passed = False
        print(f"Ineligible but has distance_value in {d['id']}")

if tests_passed:
    print("ALL INTEGRITY TESTS PASSED")
else:
    print("INTEGRITY TESTS FAILED")
