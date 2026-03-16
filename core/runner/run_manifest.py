from __future__ import annotations
import os
from datetime import datetime

class RunManifest:
    """
    Experiment Run Manifest
    Garantees reproducibility by recording all execution context.
    File: run_manifest.yaml
    """
    def __init__(
        self,
        experiment: str,
        engine: str,
        parameters: dict,
        hil_command: str,
        integrity_status: bool = True,
        helix_version: str = "1.0",
        artifact_paths: list[str] | None = None
    ):
        self.experiment = experiment
        self.engine = engine
        self.parameters = parameters
        self.timestamp = datetime.now().isoformat()
        self.helix_version = helix_version
        self.hil_command = hil_command
        self.integrity_status = integrity_status
        self.artifact_paths = artifact_paths or []

    def to_yaml(self) -> str:
        """Primitive YAML serializer to avoid external dependencies."""
        lines = [
            f"experiment: {self.experiment}",
            f"engine: {self.engine}",
            "parameters:"
        ]
        if not self.parameters:
            lines[-1] += " {}"
        else:
            for k, v in self.parameters.items():
                lines.append(f"  {k}: {v}")
        
        lines.extend([
            f"timestamp: {self.timestamp}",
            f"helix_version: {self.helix_version}",
            f"hil_command: \"{self.hil_command}\"",
            f"integrity_status: {self.integrity_status}",
            "artifact_paths:"
        ])
        if not self.artifact_paths:
            lines[-1] += " []"
        else:
            for path in self.artifact_paths:
                lines.append(f"  - {path}")
        
        return "\n".join(lines)

    def save(self, directory: str) -> str:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        path = os.path.join(directory, "run_manifest.yaml")
        with open(path, "w") as f:
            f.write(self.to_yaml())
        return path
