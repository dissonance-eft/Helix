"""
Stage 2 — Metadata normalization
==================================
Reads chip-format files (VGM/SPC/NSF/etc.) at the static parse level.
Combines internal header data with external APEv2 .tag sidecars to
produce a canonical metadata record per track.

Sidecar fields take priority over internal metadata for chip formats:
  Sound chip, Platform, Franchise, Sound Team, Featuring

Delegates to MasterPipeline stage:
  3 (tier_a_parse) — static parse of chip register headers
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from substrates.music.pipeline import MusicSubstratePipeline


def run(pipeline: "MusicSubstratePipeline") -> None:
    """Normalise metadata via static chip parse (legacy stage 3)."""
    pipeline._delegate_to_legacy([3])
