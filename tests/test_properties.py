import os
import sys
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

import engine.modules as m

def test_permutation_invariance():
    m.init_random(42)
    domains = m.load_domains()
    
    original_save = m.save_wrapped
    m.save_wrapped = lambda path, data: None
    
    try:
        out1 = m.extract_eigenspace(domains)
        random.seed(99)
        random.shuffle(domains)
        out2 = m.extract_eigenspace(domains)
        
        if out1 and out2:
            for v1, v2 in zip(out1["variance_explained"], out2["variance_explained"]):
                assert abs(v1 - v2) < 1e-9, "Permutation altered SVD structural variance explained!"
    finally:
        m.save_wrapped = original_save

    print("test_properties (permutation invariance): PASS")

if __name__ == "__main__":
    test_permutation_invariance()
