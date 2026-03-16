import numpy as np
import os
import sys
import json
from pathlib import Path

# Add REPO_ROOT to sys.path for core imports
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from labs.invariants.probe_interface import HelixProbe
from core.python_suite.analysis.feature_extractor import FeatureExtractor

class EpistemicIrreversibilityProbe(HelixProbe):
    """
    Probe: Epistemic Irreversibility
    Measures the degree to which a system's state becomes 'locked' or 'committed' 
    such that returning to a state of high entropy (undecided) is energetically 
    or information-theoretically impossible without external injection.
    """
    VERSION = "1.0.1"

    def run(self, dataset: dict) -> dict:
        """
        Simulates a bistable system undergoing a decision commitment.
        
        Parameters from dataset:
            n_samples: float  - Number of trials
            noise: float      - SDE noise intensity
            bias: float       - Initial symmetry breaking bias
            steps: int        - Simulation steps
        """
        try:
            n_samples = int(dataset.get("n_samples", 100))
            noise = float(dataset.get("noise", 0.05))
            bias = float(dataset.get("bias", 0.01))
            steps = int(dataset.get("steps", 200))
        except (ValueError, TypeError) as e:
            # Fallback or re-raise with better info
            return {
                "status": "error",
                "message": f"Parameter type mismatch in probe: {e}",
                "passed": False
            }
        dt = 0.05
        
        # System: dx/dt = x - x^3 + bias + noise*dW
        # Unstable equilibrium at x=0, stable at x=1 and x=-1
        
        results = []
        irreversibility_scores = []
        
        for trial in range(n_samples):
            x = 0.0 + bias # Start near 0
            history = [x]
            
            # Forward pass: Commitment
            for _ in range(steps):
                dx = (x - x**3 + bias) * dt + noise * np.sqrt(dt) * np.random.randn()
                x += dx
                history.append(x)
            
            # Final commitment state
            commitment = 1.0 if x > 0 else -1.0
            
            # Reverse-path test (Heuristic): 
            # How much entropy is lost? KL divergence of probability of being at x=0
            # Given we are at x=commitment, how likely are we to return to x=0 by random walk alone?
            # Pe = exp(-2 * potential_barrier / noise^2)
            # Barrier height for x - x^3 is 0.25 (integral of x-x^3 from 0 to 1)
            barrier = 0.25
            reversal_prob = np.exp(-2 * barrier / (noise**2 + 1e-9))
            
            # Info loss (bits) = -log2(reversal_prob)
            info_loss = -np.log2(reversal_prob + 1e-15)
            irreversibility_scores.append(info_loss)
            results.append(x)

        avg_irreversibility = np.mean(irreversibility_scores)
        passed = avg_irreversibility > 5.0 # Threshold for 'irreversible' commit
        
        # Extract features for Atlas
        features = FeatureExtractor.extract_all({
            "final_states": results,
            "irreversibility_distribution": irreversibility_scores
        })
        
        return {
            "probe_name": "epistemic_irreversibility",
            "signal": float(avg_irreversibility),
            "confidence": "HIGH" if passed else "LOW",
            "passed": bool(passed),
            "domain": "dynamical_systems",
            "findings": {
                "mean_info_loss_bits": float(avg_irreversibility),
                "commitment_bias": float(np.mean(results)),
                "unstable_ratio": float(np.sum(np.abs(results) < 0.5) / n_samples)
            },
            "features": features
        }

def run(params: dict) -> dict:
    """Module-level entry point for Helix Python Engine."""
    probe = EpistemicIrreversibilityProbe()
    return probe.run(params)

if __name__ == "__main__":
    # Create sample HIL-compatible input if run manually
    probe = EpistemicIrreversibilityProbe()
    if os.environ.get("HELIX_SYSTEM_INPUT"):
        probe.execute_from_env()
    else:
        # Default local run for validation
        res = probe.run({"n_samples": 50, "noise": 0.1, "bias": 0.02})
        print(json.dumps(res, indent=2))
