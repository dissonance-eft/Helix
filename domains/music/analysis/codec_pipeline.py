"""
Codec Pipeline — domains/music/analysis/codec_pipeline.py
==========================================================
The unified per-file analysis entrypoint.

Translates any supported music format into a schema-consistent TrackAnalysis.
Think of this as the "translator": many input codecs, one output schema.

Tier routing:
  VGM/VGZ   → Tier A (vgm_parser) + Tier A+ (note reconstruction) + Tier D (symbolic)
  SPC       → Tier A (spc_parser snapshot) + Tier D via SPC2MID → symbolic
  NSF/NSFe  → Tier A (nsf_parser header) + Tier D via nsf2vgm → symbolic
  SID       → Tier A (sid_parser snapshot) + Tier C (waveform)
  MP3/Opus  → Tier C (essentia/librosa waveform only)
  USF/PSF/* → Tier C (vgmstream render → essentia)

Metadata policy:
  Never reads embedded tags. All metadata joined from codex/library/music/.
"""

from __future__ import annotations

import json
import struct
import tempfile
from pathlib import Path
from typing import Any, Optional

from domains.music.analysis.track_analysis import (
    TrackAnalysis,
    ChipVoiceSnapshot,
    NoteEvent,
    StructuralSection,
    DCPProxies,
    SubstrateVector,
    WaveformFeatures,
    SymbolicFeatures,
)
from domains.music.parsing.router import FormatRouter

_router = FormatRouter()


# ---------------------------------------------------------------------------
# Substrate vector lookup: hardware ceiling per chip
# Loaded from core adapter data (static constants)
# ---------------------------------------------------------------------------

def _substrate_for_chip(chip_name: str) -> Optional[SubstrateVector]:
    """
    Return the substrate capability vector for a chip.
    This is the DCP profile of the medium — static generative ceiling.
    Values are normalised 0-1 against the highest known ceiling for each axis.
    """
    # possibility_space: max expressible pitch/timbre entropy
    # constraint:        how tightly the hardware limits output
    # attractor_stability: loop/repeat support quality
    # basin_permeability:  envelope flexibility
    # recurrence_depth:    polyphony x patch variation ceiling
    _VECTORS: dict[str, dict[str, float]] = {
        "YM2612": {
            "possibility_space":   0.90,
            "constraint":          0.85,
            "attractor_stability": 0.70,
            "basin_permeability":  0.75,
            "recurrence_depth":    0.95,
        },
        "SN76489": {
            "possibility_space":   0.25,
            "constraint":          0.30,
            "attractor_stability": 0.50,
            "basin_permeability":  0.60,
            "recurrence_depth":    0.20,
        },
        "SNES_SPC700_SDSP": {
            "possibility_space":   0.80,
            "constraint":          0.88,
            "attractor_stability": 0.65,
            "basin_permeability":  0.82,
            "recurrence_depth":    0.90,
        },
        "YM2151": {
            "possibility_space":   0.82,
            "constraint":          0.80,
            "attractor_stability": 0.68,
            "basin_permeability":  0.72,
            "recurrence_depth":    0.88,
        },
        "YM2413": {
            "possibility_space":   0.65,
            "constraint":          0.50,
            "attractor_stability": 0.60,
            "basin_permeability":  0.65,
            "recurrence_depth":    0.55,
        },
        "YM3812": {
            "possibility_space":   0.72,
            "constraint":          0.68,
            "attractor_stability": 0.62,
            "basin_permeability":  0.70,
            "recurrence_depth":    0.70,
        },
        "AY8910": {
            "possibility_space":   0.30,
            "constraint":          0.35,
            "attractor_stability": 0.48,
            "basin_permeability":  0.55,
            "recurrence_depth":    0.25,
        },
        "HuC6280": {
            "possibility_space":   0.60,
            "constraint":          0.65,
            "attractor_stability": 0.58,
            "basin_permeability":  0.62,
            "recurrence_depth":    0.65,
        },
        "NES_APU": {
            "possibility_space":   0.35,
            "constraint":          0.40,
            "attractor_stability": 0.55,
            "basin_permeability":  0.50,
            "recurrence_depth":    0.30,
        },
    }

    data = _VECTORS.get(chip_name)
    if not data:
        return None
    return SubstrateVector(chip_id=chip_name, **data)


# ---------------------------------------------------------------------------
# Library metadata join
# ---------------------------------------------------------------------------

def _join_library_metadata(file_path: Path, analysis: TrackAnalysis) -> None:
    """
    Join library metadata from codex/library/music/ into analysis.
    Match order: exact path → title+artist → filename stem.
    Adds: library_title, library_artist, library_game, library_platform,
          library_year, library_is_loved, library_meta.
    """
    # Walk up to find Helix root (contains codex/)
    root = file_path
    for _ in range(10):
        if (root / "codex").exists():
            break
        root = root.parent

    library_root = root / "codex" / "library" / "music"
    if not library_root.exists():
        return

    stem = file_path.stem.lower()
    best: Optional[dict] = None

    # Search all JSON files in library
    for json_file in library_root.rglob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            # Handle both single records and lists
            records = data if isinstance(data, list) else [data]
            for record in records:
                rec_path = str(record.get("file_path", record.get("path", ""))).lower()
                rec_title = str(record.get("title", record.get("name", ""))).lower()

                # Priority 1: exact path match
                if str(file_path).lower() in rec_path or rec_path in str(file_path).lower():
                    best = record
                    break
                # Priority 2: stem match
                if stem and stem in rec_path:
                    best = record
        except Exception:
            continue
        if best:
            break

    if not best:
        return

    analysis.library_title    = best.get("title", best.get("name", ""))
    analysis.library_artist   = best.get("artist", best.get("composer", ""))
    analysis.library_game     = best.get("game", best.get("album", ""))
    analysis.library_platform = best.get("platform", best.get("system", ""))
    analysis.library_year     = str(best.get("year", best.get("date", "")))
    analysis.library_is_loved = bool(best.get("loved", best.get("rating", 0)))
    analysis.library_meta     = best


# ---------------------------------------------------------------------------
# Tier C: waveform analysis
# ---------------------------------------------------------------------------

def _run_waveform(path: Path) -> Optional[WaveformFeatures]:
    """Run essentia (fallback: librosa) waveform analysis."""
    try:
        result = _router.waveform_analyze(path)
        if not result.get("available", False):
            return None
        return WaveformFeatures(
            bpm               = result.get("bpm"),
            key               = result.get("key"),
            key_strength      = result.get("key_strength"),
            spectral_centroid = result.get("spectral_centroid", 0.0),
            spectral_complexity = result.get("spectral_complexity", 0.0),
            dissonance        = result.get("dissonance", 0.0),
            dynamic_complexity = result.get("dynamic_complexity", 0.0),
            hfc               = result.get("hfc", 0.0),
            tonal_centroid    = result.get("tonal_centroid", [0.0] * 6),
            chord_histogram   = result.get("chord_histogram", [0.0] * 24),
            adapter           = result.get("adapter", ""),
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Tier D: symbolic analysis
# ---------------------------------------------------------------------------

def _run_symbolic(
    midi_path: Path,
    midi_source: str,
    loop_point_s: Optional[float] = None,
) -> Optional[SymbolicFeatures]:
    """
    Run symbolic MIDI analysis and return SymbolicFeatures.
    """
    from domains.music.analysis.symbolic_analyzer import analyze_midi, SymbolicAnalysis

    try:
        sa: SymbolicAnalysis = analyze_midi(midi_path, midi_source=midi_source,
                                             loop_point_s=loop_point_s)
        if sa.error:
            return None

        # Map SymbolicAnalysis → SymbolicFeatures (unified schema)
        return SymbolicFeatures(
            note_count           = sa.total_notes,
            unique_pitches       = sa.unique_pitches,
            pitch_range          = sa.pitch_range,
            pitch_center         = sa.pitch_center,
            pitch_entropy        = sa.pitch_entropy,
            avg_note_duration    = sa.duration_s / max(1, sa.total_notes),
            rhythmic_entropy     = sa.rhythmic_entropy,
            note_density         = sa.note_density,
            active_channels      = sa.active_channels,
            estimated_key        = sa.estimated_key,
            loop_start_beat      = None,  # could compute from loop_point_s × tempo
            loop_end_beat        = None,
            channel_note_counts  = sa.channel_note_counts,
            channel_pitch_ranges = sa.channel_pitch_ranges,
            midi_source          = midi_source,
            # Music theory fields (stored in library_meta for now, full schema extension TBD)
        )
    except Exception:
        return None


def _run_symbolic_full(
    midi_path: Path,
    midi_source: str,
    loop_point_s: Optional[float] = None,
) -> tuple[Optional[SymbolicFeatures], dict]:
    """Returns (SymbolicFeatures, full_symbolic_dict) for the rich music theory layer."""
    from domains.music.analysis.symbolic_analyzer import analyze_midi
    from dataclasses import asdict

    try:
        sa = analyze_midi(midi_path, midi_source=midi_source, loop_point_s=loop_point_s)
        sf = _run_symbolic(midi_path, midi_source, loop_point_s)
        return sf, asdict(sa)
    except Exception:
        return None, {}


# ---------------------------------------------------------------------------
# VGM pipeline
# ---------------------------------------------------------------------------

def _analyze_vgm(path: Path) -> TrackAnalysis:
    from domains.music.parsing.vgm_parser import parse as vgm_parse, VGMEvent

    track = vgm_parse(path)
    if track.error:
        return TrackAnalysis.error_record(path, track.error)

    h = track.header
    loop_s = (0x1C + h.loop_offset) / 44100.0 if h.loop_offset else None

    # Chip list and CCS
    chips = _vgm_chip_names(h)
    primary_chip = chips[0] if chips else ""

    analysis = TrackAnalysis(
        file_path     = str(path),
        format        = "VGM" if path.suffix.lower() == ".vgm" else "VGZ",
        chips         = chips,
        has_loop      = bool(h.loop_offset),
        loop_start_s  = loop_s,
        duration_s    = h.total_samples / 44100.0,
        analysis_tier = "A",
        confidence    = 0.7,
    )

    # Structural section: loop point
    if loop_s:
        analysis.sections.append(StructuralSection(
            time_s=0.0, label="loop_start", confidence=1.0
        ))
        analysis.sections.append(StructuralSection(
            time_s=loop_s, label="loop_seam", confidence=1.0
        ))

    # CCS vector
    if primary_chip:
        analysis.substrate = _substrate_for_chip(primary_chip)

    # Note events from register trace (Tier A+)
    # Extract key-on events from YM2612 registers
    note_events = _extract_vgm_note_events(track.events, chips)
    analysis.note_events = note_events
    if note_events:
        analysis.analysis_tier = "A+"

    # DCP proxies from loop structure
    if loop_s and note_events:
        analysis.dcp = _compute_vgm_dcp(note_events, loop_s, analysis.duration_s)

    _join_library_metadata(path, analysis)

    # Symbolic (Tier D): attempt MIDI reconstruction if vgm_note_reconstructor exists
    try:
        from domains.music.parsing.vgm_note_reconstructor import reconstruct_to_midi
        with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tf:
            midi_path = Path(tf.name)
        if reconstruct_to_midi(track, midi_path):
            sf, full = _run_symbolic_full(midi_path, "vgm_reconstructor", loop_s)
            analysis.symbolic = sf
            analysis.library_meta["symbolic_full"] = full
            analysis.analysis_tier = "A+D"
            analysis.confidence = 0.9
    except ImportError:
        pass

    return analysis


def _extract_vgm_note_events(events, chips: list[str]) -> list[NoteEvent]:
    """
    Extract note-on events from VGM register stream.
    Focuses on YM2612 key-on (reg 0x28) and PSG frequency writes.
    """
    from domains.music.parsing.vgm_parser import VGMEvent

    note_events: list[NoteEvent] = []

    # YM2612 frequency registers (block/fnum): 0xA0-0xA5 (port0), +0x100 (port1)
    # Key-on reg: 0x28
    fm_state: dict[str, dict] = {}  # ch_id → {block, fnum, op_mask, active}

    for ev in events:
        if ev.kind in ("ym2612_p0", "ym2612_p1"):
            port = 1 if ev.kind == "ym2612_p1" else 0
            ch_offset = 3 if port else 0

            # Key-on / key-off: reg 0x28
            if ev.reg == 0x28:
                ch_idx  = ev.val & 0x03
                op_mask = (ev.val >> 4) & 0x0F
                ch_id   = f"FM{ch_idx + ch_offset}"
                if ch_id not in fm_state:
                    fm_state[ch_id] = {"block": 0, "fnum": 0, "op_mask": 0,
                                       "pitch_midi": -1, "active": False}
                fm_state[ch_id]["op_mask"] = op_mask
                fm_state[ch_id]["active"]  = op_mask > 0

                if op_mask > 0 and fm_state[ch_id].get("pitch_midi", -1) >= 0:
                    note_events.append(NoteEvent(
                        time_s     = ev.time_s,
                        channel    = ch_idx + ch_offset,
                        pitch_midi = fm_state[ch_id]["pitch_midi"],
                        pitch_hz   = _midi_to_hz(fm_state[ch_id]["pitch_midi"]),
                        velocity   = 0.7,  # YM2612 TL-derived velocity would need more context
                        is_loop    = ev.is_loop,
                    ))

            # Frequency registers: set block/fnum, compute pitch
            elif 0xA4 <= ev.reg <= 0xA6:  # fnum high + block
                ch_idx = ev.reg - 0xA4
                ch_id  = f"FM{ch_idx + ch_offset}"
                if ch_id not in fm_state:
                    fm_state[ch_id] = {"block": 0, "fnum": 0, "op_mask": 0,
                                       "pitch_midi": -1, "active": False}
                fm_state[ch_id]["block"] = (ev.val >> 3) & 0x07
                fm_state[ch_id]["fnum"]  = ((ev.val & 0x07) << 8) | fm_state[ch_id].get("fnum_low", 0)
                fm_state[ch_id]["pitch_midi"] = _ym2612_to_midi(
                    fm_state[ch_id]["block"], fm_state[ch_id]["fnum"]
                )
            elif 0xA0 <= ev.reg <= 0xA2:  # fnum low
                ch_idx = ev.reg - 0xA0
                ch_id  = f"FM{ch_idx + ch_offset}"
                if ch_id not in fm_state:
                    fm_state[ch_id] = {"block": 0, "fnum": 0, "op_mask": 0,
                                       "pitch_midi": -1, "active": False}
                fm_state[ch_id]["fnum_low"] = ev.val

    return note_events


def _ym2612_to_midi(block: int, fnum: int) -> int:
    """Convert YM2612 block/fnum to approximate MIDI note."""
    if fnum == 0:
        return -1
    import math
    # f_hz = fnum × clock / (144 × 2^(20 - block))
    # YM2612 clock typically 7.67 MHz on Mega Drive
    clock = 7_670_454
    f_hz  = fnum * clock / (144 * (1 << (20 - block)))
    if f_hz <= 0:
        return -1
    midi = 69 + 12 * math.log2(f_hz / 440.0)
    return max(0, min(127, round(midi)))


def _midi_to_hz(midi: int) -> float:
    return 440.0 * (2 ** ((midi - 69) / 12.0)) if midi >= 0 else 0.0


def _vgm_chip_names(header) -> list[str]:
    chips = []
    if getattr(header, "ym2612_clock", 0):  chips.append("YM2612")
    if getattr(header, "sn76489_clock", 0): chips.append("SN76489")
    if getattr(header, "ym2151_clock", 0):  chips.append("YM2151")
    if getattr(header, "ym2413_clock", 0):  chips.append("YM2413")
    return chips


def _compute_vgm_dcp(
    note_events: list[NoteEvent],
    loop_s: float,
    duration_s: float,
) -> DCPProxies:
    """
    Compute DCP proxies from VGM note events around the loop seam.
    The loop_offset gives us an explicit structural boundary — highest
    confidence DCP event type in the music domain.
    """
    import math

    if not note_events or loop_s <= 0:
        return DCPProxies()

    # Window: final 10% before seam = pre-seam tension zone
    window = duration_s * 0.1
    seam_start = max(0.0, loop_s - window)

    pre_events  = [e for e in note_events if seam_start <= e.time_s < loop_s]
    post_events = [e for e in note_events if loop_s <= e.time_s < loop_s + 2.0]
    all_events  = note_events

    if not pre_events:
        return DCPProxies()

    # Possibility space: pitch entropy of entire track (pre-loop region)
    pre_loop_events = [e for e in all_events if not e.is_loop]
    pitches = [e.pitch_midi for e in pre_loop_events if e.pitch_midi >= 0]
    pc_counts = [pitches.count(p % 12) for p in range(12)]
    total = sum(pc_counts)
    poss = -sum((c/total)*math.log2(c/total) for c in pc_counts if c > 0) / math.log2(12) if total else 0.0

    # Collapse: sharpness of density change at loop seam
    pre_density  = len(pre_events) / max(0.01, window)
    overall_density = len(all_events) / max(0.01, duration_s)
    collapse = min(1.0, max(0.0, pre_density / max(0.01, overall_density) - 1.0) / 2.0)

    # Tension: active channels in pre-seam window
    pre_channels = len({e.channel for e in pre_events})
    all_channels = len({e.channel for e in all_events})
    tension = pre_channels / max(1, all_channels)

    # Post-narrowing: channel count drop after seam
    post_channels = len({e.channel for e in post_events}) if post_events else 1
    post_narrow = max(0.0, 1.0 - (post_channels / max(1, pre_channels)))

    # Composite
    components = [poss, collapse, tension, post_narrow]
    available  = [c for c in components if c > 0]
    composite  = sum(available) / len(available) if available else 0.0

    qual = "FULL" if len(available) >= 4 else ("UNCONFIRMED" if len(available) >= 2 else "INSUFFICIENT")

    return DCPProxies(
        possibility_space = poss,
        collapse          = collapse,
        tension           = tension,
        post_narrowing    = post_narrow,
        composite         = composite,
        qualification     = qual,
    )


# ---------------------------------------------------------------------------
# SPC pipeline
# ---------------------------------------------------------------------------

def _analyze_spc(path: Path) -> TrackAnalysis:
    from domains.music.parsing.spc_parser import parse as spc_parse
    from core.adapters.adapter_snes_spc import VOICE_COUNT, PITCH_FREQ_FORMULA

    spc = spc_parse(path)

    analysis = TrackAnalysis(
        file_path     = str(path),
        format        = "SPC",
        chips         = ["SNES_SPC700_SDSP"],
        voice_count   = VOICE_COUNT,  # 8
        analysis_tier = "A",
        confidence    = 0.5,
        substrate     = _substrate_for_chip("SNES_SPC700_SDSP"),
    )

    # Extract voice snapshots from DSP register state
    if hasattr(spc, "voices") and spc.voices:
        for v in spc.voices:
            pitch_hz = v.get("pitch_raw", 0) * 32000 / 0x1000
            midi = _hz_to_midi(pitch_hz)
            analysis.voices.append(ChipVoiceSnapshot(
                voice_index  = v.get("index", 0),
                active       = v.get("kon", False),
                pitch_raw    = v.get("pitch_raw", 0),
                pitch_hz     = pitch_hz,
                pitch_midi   = midi,
                vol_l        = v.get("vol_l", 0) / 127.0,
                vol_r        = v.get("vol_r", 0) / 127.0,
                adsr_enabled = v.get("adsr_enabled", False),
                attack       = v.get("ar", 0),
                decay        = v.get("dr", 0),
                sustain      = v.get("sl", 0),
                release      = v.get("sr", 0),
                srcn         = v.get("srcn", 0),
            ))
        analysis.active_voices = sum(1 for v in analysis.voices if v.active)

    # SPC has no explicit loop point in the header — loop detection requires emulation
    analysis.sections.append(StructuralSection(
        time_s=0.0, label="snapshot", confidence=1.0,
    ))

    _join_library_metadata(path, analysis)

    # Tier D: SPC2MID
    analysis = _try_spc2mid(path, analysis)

    return analysis


def _hz_to_midi(hz: float) -> int:
    import math
    if hz <= 0:
        return -1
    m = 69 + 12 * math.log2(hz / 440.0)
    return max(0, min(127, round(m)))


def _try_spc2mid(path: Path, analysis: TrackAnalysis) -> TrackAnalysis:
    """
    Attempt SPC → MIDI via SPC2MID binary.
    SPC2MID is engine-specific. We try SNESNint (N-SPC, Nintendo) first
    as it covers the most SNES titles, then fall back to other binaries.

    Binary lookup order (from PATH or Helix tools/ directory):
      SNESNint.exe, SNESCapcom.exe, SNESSculpt.exe, SNESDW.exe, etc.
    """
    import shutil, subprocess

    spc2mid_binaries = [
        "SNESNint",     # Nintendo N-SPC (most common: FF, DQ, Zelda, Kirby, etc.)
        "SNESCapcom",   # Capcom (Mega Man X, Street Fighter)
        "SNESSculpt",   # Sculptured Software (Mortal Kombat)
        "SNESDW",       # David Whittaker
        "SNESKAZe",     # KAZe / Meldac
    ]

    midi_path = None
    used_binary = None

    for binary in spc2mid_binaries:
        bin_path = shutil.which(binary) or shutil.which(binary + ".exe")
        if not bin_path:
            # Also check Helix tools/ dir
            helix_tool = Path(__file__).parents[3] / "tools" / "spc2mid" / (binary + ".exe")
            if helix_tool.exists():
                bin_path = str(helix_tool)

        if bin_path:
            with tempfile.NamedTemporaryFile(suffix=".mid", delete=False) as tf:
                out_path = Path(tf.name)
            try:
                result = subprocess.run(
                    [bin_path, str(path), str(out_path)],
                    capture_output=True, timeout=30
                )
                if out_path.exists() and out_path.stat().st_size > 128:
                    midi_path = out_path
                    used_binary = binary
                    break
            except Exception:
                pass

    if midi_path:
        sf, full = _run_symbolic_full(midi_path, f"spc2mid_{used_binary}", loop_point_s=None)
        if sf:
            analysis.symbolic = sf
            analysis.library_meta["symbolic_full"] = full
            analysis.library_meta["spc2mid_binary"] = used_binary
            analysis.analysis_tier = "A+D"
            analysis.confidence = 0.82

    return analysis


# ---------------------------------------------------------------------------
# NSF pipeline
# ---------------------------------------------------------------------------

def _analyze_nsf(path: Path) -> TrackAnalysis:
    from domains.music.parsing.nsf_parser import parse as nsf_parse

    nsf = nsf_parse(path)

    analysis = TrackAnalysis(
        file_path     = str(path),
        format        = "NSF",
        chips         = _nsf_chip_names(nsf),
        analysis_tier = "A",
        confidence    = 0.4,
        substrate     = _substrate_for_chip("NES_APU"),
    )

    _join_library_metadata(path, analysis)
    return analysis


def _nsf_chip_names(nsf) -> list[str]:
    chips = ["NES_APU"]
    flags = getattr(nsf, "extra_sound_chip", 0) if hasattr(nsf, "extra_sound_chip") else \
            (nsf.to_dict().get("extra_sound_chip", 0) if hasattr(nsf, "to_dict") else 0)
    if flags & 0x01: chips.append("VRC6")
    if flags & 0x02: chips.append("VRC7")
    if flags & 0x04: chips.append("FDS")
    if flags & 0x08: chips.append("MMC5")
    if flags & 0x10: chips.append("N163")
    if flags & 0x20: chips.append("Sunsoft5B")
    return chips


# ---------------------------------------------------------------------------
# SID pipeline
# ---------------------------------------------------------------------------

def _analyze_sid(path: Path) -> TrackAnalysis:
    from domains.music.parsing.sid_parser import parse as sid_parse

    sid = sid_parse(path)
    d   = sid.to_dict() if hasattr(sid, "to_dict") else {}

    analysis = TrackAnalysis(
        file_path     = str(path),
        format        = "SID",
        chips         = ["SID_6581" if d.get("sid_model") == "6581" else "SID_8580"],
        voice_count   = 3,
        analysis_tier = "A",
        confidence    = 0.5,
    )

    # Voice snapshots from SID register state
    for vi in range(3):
        vkey = f"voice{vi + 1}"
        if vkey in d:
            v = d[vkey]
            freq_hz = v.get("frequency_hz", 0.0)
            analysis.voices.append(ChipVoiceSnapshot(
                voice_index  = vi,
                active       = v.get("gate", False),
                pitch_raw    = v.get("frequency_raw", 0),
                pitch_hz     = freq_hz,
                pitch_midi   = _hz_to_midi(freq_hz),
                vol_l        = d.get("master_volume", 15) / 15.0,
                vol_r        = d.get("master_volume", 15) / 15.0,
                adsr_enabled = True,
                attack       = v.get("attack", 0),
                decay        = v.get("decay", 0),
                sustain      = v.get("sustain", 0),
                release      = v.get("release", 0),
                waveform     = v.get("waveform", ""),
            ))

    _join_library_metadata(path, analysis)

    # SID: waveform path (reSID render) — symbolic not supported yet
    wav = _run_waveform(path)
    if wav:
        analysis.waveform = wav
        analysis.analysis_tier = "A+C"
        analysis.confidence = 0.65

    return analysis


# ---------------------------------------------------------------------------
# Waveform-only pipeline (MP3, Opus, FLAC, etc.)
# ---------------------------------------------------------------------------

def _analyze_waveform(path: Path) -> TrackAnalysis:
    analysis = TrackAnalysis(
        file_path     = str(path),
        format        = path.suffix.lstrip(".").upper(),
        analysis_tier = "C",
        confidence    = 0.4,
    )

    wf = _run_waveform(path)
    if wf:
        analysis.waveform = wf
        analysis.confidence = 0.55
    else:
        analysis.error = "waveform analysis unavailable (essentia not installed)"
        analysis.confidence = 0.0

    _join_library_metadata(path, analysis)
    return analysis


# ---------------------------------------------------------------------------
# Render-then-analyze pipeline (USF, PSF, mini*)
# ---------------------------------------------------------------------------

def _analyze_render(path: Path) -> TrackAnalysis:
    """
    Render via vgmstream to a temp WAV, then run waveform analysis.
    Waveform only — no chip data available.
    """
    import shutil, subprocess

    analysis = TrackAnalysis(
        file_path     = str(path),
        format        = path.suffix.lstrip(".").upper(),
        analysis_tier = "C",
        confidence    = 0.3,
    )

    vgmstream = shutil.which("vgmstream-cli") or shutil.which("vgmstream_cli")
    if not vgmstream:
        analysis.error = "vgmstream-cli not found; cannot render"
        _join_library_metadata(path, analysis)
        return analysis

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        wav_path = Path(tf.name)

    try:
        subprocess.run(
            [vgmstream, "-o", str(wav_path), str(path)],
            capture_output=True, timeout=60
        )
        if wav_path.exists() and wav_path.stat().st_size > 1024:
            wf = _run_waveform(wav_path)
            if wf:
                analysis.waveform = wf
                analysis.confidence = 0.4
    except Exception as e:
        analysis.error = str(e)
    finally:
        try:
            wav_path.unlink()
        except Exception:
            pass

    _join_library_metadata(path, analysis)
    return analysis


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze(file_path: str | Path) -> TrackAnalysis:
    """
    Analyze a music file. Returns a schema-consistent TrackAnalysis.
    Dispatches to the appropriate tier based on file extension.

    Call this — NOT the individual tier functions.
    """
    path = Path(file_path)
    if not path.exists():
        return TrackAnalysis.error_record(path, f"File not found: {path}")

    ext = path.suffix.lower()

    try:
        if ext in (".vgm", ".vgz", ".gym"):
            return _analyze_vgm(path)
        elif ext == ".spc":
            return _analyze_spc(path)
        elif ext in (".nsf", ".nsfe"):
            return _analyze_nsf(path)
        elif ext in (".sid", ".psid", ".rsid"):
            return _analyze_sid(path)
        elif ext in (".mp3", ".opus", ".flac", ".ogg", ".wav", ".m4a", ".aac"):
            return _analyze_waveform(path)
        elif ext in (".usf", ".miniusf", ".psf", ".psf2", ".minipsf",
                     ".2sf", ".mini2sf", ".ncsf", ".minincsf",
                     ".gsf", ".ssf", ".dsf"):
            return _analyze_render(path)
        else:
            # Unknown: try waveform fallback
            return _analyze_waveform(path)

    except Exception as e:
        return TrackAnalysis.error_record(path, str(e))


def analyze_batch(
    paths: list[str | Path],
    progress: bool = True,
) -> list[TrackAnalysis]:
    """Analyze a list of files. Returns results in the same order."""
    results = []
    total = len(paths)
    for i, p in enumerate(paths):
        if progress:
            print(f"[{i+1}/{total}] {Path(p).name}", flush=True)
        results.append(analyze(p))
    return results
