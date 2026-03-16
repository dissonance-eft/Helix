from __future__ import annotations
import json
import os
import time
import platform

class MetadataLogger:
    """
    Creates runtime metadata file: metadata.json
    """
    @staticmethod
    def log(
        directory: str,
        runtime_duration: float,
        engine_used: str,
        parameter_values: dict,
        execution_status: str
    ) -> str:
        data = {
            "runtime_duration": f"{runtime_duration:.4f}s",
            "engine_used": engine_used,
            "parameter_values": parameter_values,
            "system_environment": {
                "os": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "machine": platform.machine(),
                "python_version": platform.python_version()
            },
            "execution_status": execution_status,
            "timestamp": time.time()
        }
        
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            
        path = os.path.join(directory, "metadata.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return path
