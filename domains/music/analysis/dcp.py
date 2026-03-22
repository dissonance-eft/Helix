"""
Music Domain DCP Hook — domains/music/analysis/dcp.py
======================================================
Translates music structural features into DCP events.

Mirrors the architecture of domains/math/analysis/dcp.py.

The music DCP interpretation reads the library's structural
signals (from Spotify metadata) and maps them onto the five
DCP component proxies. The canonical collapse event in music
is the LOOP-SEAM — the moment where a developing structural
trajectory returns to a known state, creating a circular-
collapse-like compression event.

This module does two things:
  1. Emit DCP metadata-level candidate events from Spotify
     track records (what we can measure now)
  2. Define the full DCP event structure for audio-level
     loop-seam probes (what is deferred until audio access)

Layer relationships:
  domains/music/pattern_detection/motif_discovery.py  → motif-level patterns
  domains/music/analysis/loop_seam.py                 → loop-seam probe (candidacy)
  domains/music/analysis/dcp.py    ← THIS FILE         → DCP event emission
  core/invariants/dcp/event.py                        → canonical event schema
  core/invariants/dcp/metrics.py                      → metric functions

Limitation notes embedded throughout.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

ROOT = next(
    p for p in Path(__file__).resolve().parents
    if (p / "MANIFEST.yaml").exists()
)
sys.path.insert(0, str(ROOT))

from core.invariants.dcp.event import DCPEvent
from core.invariants.dcp.metrics import compute_dcp_score


# ─── DCP component mapping for music domain ──────────────────────────────────
#
# possibility_space_proxy:
#   Breadth of harmonic / structural futures before the collapse.
#   Proxy: 1 - Instrumentalness (vocal tracks) or track energy spread.
#   High instrumentalness + low speechiness → richer structural vocabulary.
#   Formula: (1 - instrumentalness) * energy_normalized
#   Limitation: this is a very indirect proxy. Does not measure actual
#   harmonic breadth. Requires audio-level analysis to do properly.
#
# constraint_proxy:
#   Structural constraint acting on the possibility space.
#   Proxy: liveness inverted (low liveness = high production constraint =
#          more structured/constrained arrangement) + tempo stability
#          (Spotify doesn't provide tempo variance — single value only).
#   Formula: 1 - liveness
#   Limitation: liveness ≠ structural constraint. Plausible correlation only.
#
# tension_proxy:
#   Pre-collapse unresolved competition.
#   Proxy: valence inversion weighted by energy.
#   Low valence + high energy = unresolved emotional/structural tension.
#   Formula: (1 - valence) * energy
#   Limitation: emotional tension (valence) is not the same as structural
#   tension (pre-seam harmonic or rhythmic pressure). Acceptable metadata
#   approximation until audio analysis is available.
#
# collapse_proxy:
#   Sharpness of the compression event.
#   CANNOT BE ESTIMATED FROM SPOTIFY METADATA.
#   Spotify provides aggregate track-level features only — no time-series.
#   A loop-seam is a time-specific event; without onset or structure data
#   from the waveform, collapse sharpness is not measurable.
#   Returns None — qualification_status() will reflect this.
#
# post_collapse_narrowing:
#   Reduction in trajectory diversity after the seam.
#   Proxy: high recurrence structures → low post-seam diversity.
#   Approximated from instrumentalness and energy stability.
#   Formula: instrumentalness * (1 - valence_variance_proxy)
#   Note: valence_variance is not available per-track from Spotify.
#         Using instrumentalness alone as post-seam narrowing proxy.
#   Limitation: significant approximation. Low confidence.


def extract_dcp_event_from_spotify(
    track: dict[str, Any],
    source_artifact: str = "spotify_library",
) -> DCPEvent:
    """
    Emit a music-domain DCP event from a single Spotify track record.

    This is a METADATA-LEVEL event — it uses only what Spotify provides.
    collapse_proxy is explicitly None because sharpness requires audio.

    Args:
        track: a single record from the Spotify JSON library
                (fields: Track Name, Artist Name(s), Energy, Valence,
                 Instrumentalness, Liveness, Danceability, Acousticness,
                 Speechiness, Tempo, etc.)
        source_artifact: artifact identifier for provenance

    Returns:
        DCPEvent with qualification_status UNCONFIRMED (collapse_proxy=None)
        or INCOMPLETE depending on available fields.
    """
    def _get(key: str, default: float = 0.0) -> float:
        v = track.get(key)
        try:
            return float(v) if v is not None else default
        except (TypeError, ValueError):
            return default

    energy           = _get("Energy")
    valence          = _get("Valence")
    instrumentalness = _get("Instrumentalness")
    liveness         = _get("Liveness")
    speechiness      = _get("Speechiness")
    acousticness     = _get("Acousticness")
    danceability     = _get("Danceability")
    tempo            = _get("Tempo", 120.0)

    # --- Possibility space ---
    # Tracks with more expressive vocabulary (not purely speech, not purely noise)
    # are considered to have broader structural possibility space.
    possibility_space = float(min(1.0, max(0.0,
        energy * (1.0 - 0.5 * speechiness)
    )))

    # --- Constraint proxy ---
    # Low liveness = high production constraint = more deterministic structure.
    constraint = float(min(1.0, max(0.0, 1.0 - liveness)))

    # --- Tension proxy ---
    # Unresolved emotional/structural tension before potential collapse.
    tension = float(min(1.0, max(0.0, (1.0 - valence) * energy)))

    # --- Collapse proxy ---
    # CANNOT BE MEASURED FROM METADATA.
    # A loop-seam is a time-specific event. Returning None is the honest choice.
    collapse = None  # type: Optional[float]

    # --- Post-collapse narrowing ---
    # Instrumental + low valence → tends toward locked, narrow post-seam state.
    # This is the weakest proxy here — significant uncertainty.
    post_narrowing = float(min(1.0, max(0.0,
        instrumentalness * 0.5 + (1.0 - valence) * 0.5
    )))

    # Composite score (collapse is missing — qualification will be UNCONFIRMED)
    dcp_score = compute_dcp_score(
        possibility_space=possibility_space,
        constraint=constraint,
        tension=tension,
        collapse=collapse,
        post_narrowing=post_narrowing,
    )

    # Confidence: capped lower than math hook since collapse is entirely absent
    confidence = float(min(0.45, dcp_score * 0.5))

    track_name  = track.get("Track Name", "unknown")
    artist_name = track.get("Artist Name(s)", "unknown")
    track_uri   = track.get("Track URI", "")

    event_id = f"music.dcp.spotify.{track_uri.split(':')[-1]}" if track_uri else f"music.dcp.{track_name[:20]}"

    return DCPEvent(
        source_domain="music",
        source_artifact=source_artifact,
        event_id=event_id,
        possibility_space_proxy=possibility_space,
        constraint_proxy=constraint,
        tension_proxy=tension,
        collapse_proxy=collapse,          # None — requires audio
        post_collapse_narrowing=post_narrowing,
        confidence=confidence,
        calibration_status="provisional",
        notes=(
            f"Track: '{track_name}' by {artist_name}. "
            f"Metadata-level proxy only. collapse_proxy=None "
            f"(requires audio-level loop-seam detection). "
            f"See domains/music/analysis/loop_seam.py for candidacy scoring."
        ),
        domain_metadata={
            "track_name":        track_name,
            "artist":            artist_name,
            "track_uri":         track_uri,
            "energy":            energy,
            "valence":           valence,
            "instrumentalness":  instrumentalness,
            "liveness":          liveness,
            "danceability":      danceability,
            "acousticness":      acousticness,
            "speechiness":       speechiness,
            "tempo":             tempo,
            "dcp_composite":     round(dcp_score, 4),
        },
    )

