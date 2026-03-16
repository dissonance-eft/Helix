from __future__ import annotations
import importlib
from typing import Any

class EngineRegistry:
    """
    Registry for Helix execution engines.
    Resolves engine names to their respective adapters.
    """
    _REGISTRY = {
        "python": "engines.python.engine_adapter.PythonAdapter",
        "godot": "engines.godot.engine_adapter.GodotAdapter"
    }
    
    _INSTANCES: dict[str, Any] = {}

    @classmethod
    def get_engine(cls, name: str) -> Any:
        if name in cls._INSTANCES:
            return cls._INSTANCES[name]
        
        if name not in cls._REGISTRY:
            return None
            
        module_path, class_name = cls._REGISTRY[name].rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
            adapter_class = getattr(module, class_name)
            instance = adapter_class()
            cls._INSTANCES[name] = instance
            return instance
        except (ImportError, AttributeError) as e:
            print(f"[EngineRegistry] Failed to load engine '{name}': {e}")
            return None

    @classmethod
    def list_engines(cls) -> list[str]:
        return list(cls._REGISTRY.keys())
