# Music Domain — Helix Analysis Pipeline

**Location**: `domains/music/`  
**Updated**: 2026-03-20

---

## Vision

The music domain treats every supported audio format — whether a native chip
register dump, a PSF container, or a rendered MP3 — as **input to a unified
codec**. The goal is a schema-consistent `TrackAnalysis` output regardless of
the original format, similar to how a translator takes many source languages
and produces a normalised output.

The key insight is that **emulated formats are better than sheet music** for
analysis purposes. A VGM file is a hardware-accurate register trace — the
complete, deterministic record of every note, volume change, timbre switch,
and timing event. A SPC file is a 64KB RAM + DSP snapshot of a running SNES
audio program. These are equivalent to having the conductor's score, the
individual parts, and the performance notes simultaneously. MP3 and Opus are
only the final waveform — the equivalent of a recording. The pipeline
exploits this hierarchy.

---

## Metadata Policy

> **Never read embedded tags. Use the library.**

ID666 (SPC), GD3 (VGM), ID3 (MP3), and Vorbis comments are intentionally
**not used** as metadata sources. These formats have inconsistent encoding,
poor Unicode support, and no canonical schema.

The `codex/library/music/` tree was seeded from Foobar2000's external tag
system, which supported custom fields and robust Unicode. Every track that
entered the library from `loved.m3u8` has a library record. The analysis
pipeline joins by file path/title to retrieve:

- Artist, game, platform, year
- `is_loved` taste signal
- Any custom fields written during the library seeding phase

---

## Analysis Tiers

| Tier | What | Formats | Output |
|------|------|---------|--------|
| **A** | Static parse from file header / DSP snapshot | VGM, SPC, NSF, SID | Voice snapshots, chip config, loop point, structural header |
| **A+** | Note reconstruction from register trace | VGM (native parse) | Per-channel note events with timestamps, pitch, velocity |
| **B** | Emulation chip-state trace | SPC → GME, VGM → libvgm | Full register trace for MIDI reconstruction |
| **C** | Waveform analysis | MP3, Opus, FLAC, USF/PSF renders | Essentia: BPM, key, spectral, tonal |
| **D** | Symbolic / MIDI | VGM → reconstructor, SPC → SPC2MID/VGMTrans, NSF → nsf2vgm | Sheet-music-level features |

### The "Sheet Music" View (Tier D)

For emulated formats, MIDI reconstruction is the musicologist's view — what
a human analyst would read on sheet music. This is a key advantage of
emulated music over waveform-only formats:

- **VGM** → `vgm_note_reconstructor.py` (built-in, no external binary)
- **SPC** → [SPC2MID](https://github.com/turboboy215/SPC2MID) (engine-specific
  converters: N-SPC, Capcom, Konami, etc.) or
  [VGMTrans](https://github.com/vgmtrans/vgmtrans) (24 driver families)
- **NSF** → `nsf2vgm` binary (in repo) → VGM reconstructor
- **SID** → waveform only (reSID render) — register state available but
  ADSR envelope interactions make per-note MIDI extraction non-trivial
- **USF/PSF/mini\*** → vgmstream render → essentia (waveform only for now)

MIDI is **not the end goal** — it is an intermediate representation that
enables feature extraction by the music21 / pretty_midi parsers already
in the stack.

---

## DCP Analysis

Every `TrackAnalysis` carries five DCP component proxies mapped from
chip-level or waveform measurements:

| Proxy | Music mapping |
|-------|--------------|
| `possibility_space` | Pitch entropy (pre-loop pitch distribution) |
| `constraint` | Register saturation (fraction of voices in use) |
| `tension` | Pre-loop-seam ENVX/volume variance elevation |
| `collapse` | Sharpness of the loop boundary (beat/section transition) |
| `post_narrowing` | Post-seam pitch/volume range reduction |

For VGM files, the loop_offset field in the header provides an explicit
structural boundary — the loop seam is physically marked in the binary.
This makes VGM one of the highest-confidence DCP event candidates in the
music domain.

---

## CCS Hardware Capability Vectors (6-axis)

Each chip's **hardware ceiling** is described by a 6-element vector,
pre-computed from chip adapter constants (`core/adapters/adapter_*.py`).
This vector is attached to every `TrackAnalysis` based on which chip the
file uses.

| Axis | What it measures |
|------|------------------|
| **Structural Density** | max simultaneous voices × max envelope rate |
| **Control Entropy** | pitch resolution × volume resolution × waveform count |
| **Generative Constraint** | 12-TET coverage fraction (how much of equal temperament is reachable) |
| **Attractor Stability** | loop support in driver + hardware repeat registers |
| **Basin Permeability** | key-on delay + envelope release floor |
| **Recurrence Depth** | polyphony × available timbres (upper bound on layering) |

The **gap between the chip ceiling and the corpus median** is the
*composer constraint index* — how much of the chip's expressible space is
actually used. This is a core Helix research direction (R1 in
`codex/library/tech/sound_chip/README.md`).

---

## Adapter Reference

### Tier A parsers (`domains/music/parsing/`)

| File | Format | Extracts |
|------|--------|---------|
| `vgm_parser.py` | VGM/VGZ | Full command stream (144-command spec table), loop_offset tagged, timestamps per event. GD3 skipped. |
| `spc_parser.py` | SPC | DSP register snapshot: 8 voices, ADSR, KON/KOFF, echo, FIR. ID666 skipped. |
| `nsf_parser.py` | NSF/NSFe | Header: chip flags, expansion chips, song count, addresses |
| `sid_parser.py` | PSID/RSID | Voice snapshot, filter state, waveform distribution, multi-SID count |

### Feature extraction (`domains/music/feature_extraction/`)

| File | Input | Extracts |
|------|-------|---------|
| `feature_extractor.py` | VGMTrack | Per-channel key-on counts, pitch histogram, pitch entropy, algorithm/feedback distribution, TL analysis, rhythmic entropy, loop event index |
| `channel_profiler.py` | Event DataFrame | Channel role inference (bass/melody/percussion/atmospheric) |

### Analysis (`domains/music/analysis/`)

| File | Purpose |
|------|---------|
| `track_analysis.py` | Unified output schema (`TrackAnalysis` dataclass) |
| `dcp.py` | Maps Spotify/structural features to DCP events |
| `loop_seam.py` | Metadata-level loop-seam candidacy scoring |
| `loop_seam_audio.py` | Spotify audio analysis → DCP collapse_proxy |

### Core adapters (`core/adapters/`) — chip constants

All `adapter_*.py` files are **static constants only**, no Helix logic.
Full adapters provide register maps, timing constants, operator layouts,
and driver conventions for: YM2612 (OPN2), YM2151 (OPM), YM3812/YMF262
(OPL2/3), YM2413 (OPLL/VRC7), SN76489 (PSG), AY-3-8910 (PSG),
NES APU (2A03/2A07), SNES S-DSP + SPC700, Game Boy DMG APU, RF5C68/164.

See `codex/library/tech/sound_chip/README.md` for full coverage map and
research directions.

---

## Ingestion (`domains/music/ingestion/`)

### loved.m3u8 pipeline

The primary test corpus is `C:\Users\dissonance\Desktop\loved.m3u8` —
the Foobar2000 "Loved" playlist. This M3U8 file contains absolute paths
to local files across many formats. The pipeline:

1. Parse M3U8 → absolute file paths
2. For each path: `FormatRouter.route()` → Tier
3. Tier A: static parse → `TrackAnalysis` (chip/structure layer)
4. Tier B (if SPC/NSF): GME emulation → MIDI reconstruction
5. Tier C (if waveform): essentia → waveform features
6. Library join: match path to `codex/library/music/` → inject metadata
7. DCP proxy computation from available features
8. CCS vector attachment from chip adapter
9. Emit `TrackAnalysis` to output

### Metadata join rule

Match priority:
1. Exact file path match in library record
2. Title + artist match (normalised, case-insensitive)
3. Filename stem match (last resort)

---

---

## Toolset Evaluation

### Current stack (confirmed correct)

| Tool | Role | Notes |
|------|------|-------|
| `music21` | Harmonic analysis, chord progression, key detection | Gold standard. `.chordify()` + `romanNumeralFromChord()` gives proper ii6, V7/IV etc — far better than naive triad matching |
| `pretty_midi` | Fast MIDI note extraction (fallback) | Good for raw note stats. Slower than symusic for large files |
| `essentia` | Waveform audio descriptors | Best general audio feature extractor. BPM, key, spectral, tonal |
| `librosa` | Waveform fallback | Decent chroma/BPM, much lighter than essentia |
| `vgm_parser` (custom) | VGM register stream parsing | Nothing better in Python. Spec-accurate with full 144-command table |
| `SPC2MID` binaries | SPC → MIDI extraction | Engine-specific = highest accuracy. Try N-SPC first |

### Upgrade path (not blocking, but worth noting)

**`madmom`** — deep learning beat/downbeat tracker. Currently we use IOI bucketing for tempo and phrase detection, which is a weak heuristic. Madmom's `DBNBeatTracker` would give:
- Accurate BPM (not just dominant IOI)
- **Downbeat positions** (bar-starts, not just beats) → real 4-bar phrase detection
- Better rhythmic entropy measurements

Install when ready: `pip install madmom`. Will auto-activate in `symbolic_analyzer.py` if present (no code changes needed, just add the import path).

**`symusic`** — Rust-backed MIDI parser, ~10-100x faster than pretty_midi for large batch processing. Drop-in for the raw note loading step when batch size gets large.

Install when ready: `pip install symusic`.

---

## Composer Attribution Research

A primary research application of this pipeline is **data-driven composer attribution** for disputed soundtracks.

The flagship case is **Sonic the Hedgehog 3 & Knuckles (1994)** — one of the most contested attributions in game music history, involving an uncredited Michael Jackson / Brad Buxer contribution and a Japanese Sega Sound Team whose per-track credits are largely guesswork.

The symbolic analysis layer extracts exactly the features that distinguish composer style:
- Harmonic language (mode, chord progressions, cadence patterns)
- Melodic fingerprint (contour, motif recurrence, interval preferences)
- Rhythmic character (groove score, syncopation, pulse coherence)
- FM synthesis fingerprint (YM2612 algorithm preference, operator programming style)

By training on **confirmed works** (Maeda/Sonic 1+2, Drossin/Comix Zone+S&K, Senoue/Sonic 3D, Buxer/Ice Cap source) and scoring disputed tracks, we can move from "it sounds like Maeda" to "here are 7 measurable structural reasons with a 0.81 confidence score."

Full research plan: see `docs/research/s3k_composer_attribution.md`

---

## What's Still Needed

Before running the full `loved.m3u8` analysis, the following are pending
(give the go when ready):

| Item | Status |
|------|--------|
| `run_loved_playlist.py` | ✅ Built — `applications/music/run_loved_playlist.py` |
| `codec_pipeline.py` | ✅ Built — `domains/music/analysis/codec_pipeline.py` |
| `symbolic_analyzer.py` | ✅ Built — music21 chordify + 7-mode + all music theory features |
| `track_analysis.py` | ✅ Built — unified output schema |
| Library metadata joiner | ✅ Built — in codec_pipeline |
| CCS vector computation | ✅ Built — pre-computed per chip in codec_pipeline |
| SPC2MID binaries in PATH or `tools/spc2mid/` | **Needs binaries** — download from [SPC2MID releases](https://github.com/turboboy215/SPC2MID/releases) |
| essentia installed | **Not found** — `pip install essentia` |
| madmom (optional but recommended) | **Not found** — `pip install madmom` |
| Say GO | Waiting |
