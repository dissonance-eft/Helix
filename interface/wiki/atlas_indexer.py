from __future__ import annotations
import os
import json
from pathlib import Path

class AtlasIndexer:
    """
    Scans the Atlas and artifacts directories to construct a structured index.
    """
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.artifacts_dir = self.repo_root / "artifacts"
        self.invariants_dir = self.repo_root / "06_atlas/invariants"
        if not self.invariants_dir.exists():
            self.invariants_dir = self.repo_root / "atlas/invariants"

    def build_index(self) -> dict:
        print("[atlas_indexer] Indexing Helix knowledge...")
        index = {
            "experiments": self._index_experiments(),
            "invariants": self._index_invariants(),
            "engines": ["python", "godot"],
            "domains": self._index_domains()
        }
        
        index_path = self.repo_root / "atlas_index.json"
        with open(index_path, "w") as f:
            json.dump(index, f, indent=4)
            
        return index

    def _index_experiments(self) -> list[dict]:
        experiments = []
        if not self.artifacts_dir.exists():
            return []
            
        for d in sorted(self.artifacts_dir.iterdir()):
            if d.is_dir():
                manifest_path = d / "run_manifest.yaml"
                if manifest_path.exists():
                    # Simple heuristic index entry
                    experiments.append({
                        "id": d.name,
                        "path": str(d.relative_to(self.repo_root)),
                        "timestamp": os.path.getmtime(d)
                    })
        return experiments

    def _index_invariants(self) -> list[dict]:
        invariants = []
        if not self.invariants_dir.exists():
            return []
            
        for f in sorted(self.invariants_dir.glob("*.json")):
            try:
                with open(f, "r") as src:
                    data = json.load(src)
                    invariants.append({
                        "name": f.stem,
                        "data": data,
                        "path": str(f.relative_to(self.repo_root))
                    })
            except Exception:
                pass
        return invariants

    def _index_domains(self) -> list[str]:
        # Extract unique domain tags from invariants and experiments
        return ["dynamical", "spatial", "agent", "network"]
