# Helix Games Substrate

**Status: Planned / Stub**

The Games substrate will provide library scanning, ROM analysis, gameplay structure extraction, and knowledge graph integration over game libraries.

## Planned Pipeline Stages

| Stage | Name | Description |
|-------|------|-------------|
| 1 | `library_ingestion` | Scan and ingest game library metadata |
| 2 | `rom_analysis` | ROM header parsing, platform detection |
| 3 | `gameplay_extraction` | Gameplay mechanic and structure extraction |
| 4 | `asset_analysis` | Sprite, tile, audio asset cataloguing |
| 5 | `narrative_analysis` | Story structure, dialogue, world-building |
| 6 | `knowledge_graph` | Entity registry + graph integration |
| 7 | `llm_interpretation` | LLM-assisted interpretation |

## Entry Point

```python
from substrates.games.pipeline import GamesSubstratePipeline
```
