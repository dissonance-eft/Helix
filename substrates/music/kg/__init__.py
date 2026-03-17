"""
substrates.music.kg — Knowledge graph integration modules.

Stages:
  9  graph_integration — populate entity registry + entity graph
                          write atlas/entities/{ns}/{type}/{slug}.json
                          write atlas/music/library_index.json
"""
from .entity_builder   import build_entities
from .graph_integration import run
from .library_index    import build_library_index

__all__ = ["build_entities", "run", "build_library_index"]
