"""
domains.music.ingestion — Library ingestion and metadata normalization.

Stages:
  1  library_scanner      — scan filesystem, ingest track records
  2  metadata_normalizer  — chip register parse + sidecar processing
  3  adapters/            — source-specific adapters (Spotify, VGM, etc.)
"""

__all__ = ["library_scanner", "metadata_normalizer", "adapters"]
