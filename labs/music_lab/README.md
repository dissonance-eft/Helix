# HELIX MUSIC SUBSTRATE

The Music Substrate is the Helix environment responsible for analyzing music as a structured system.

Music combines multiple layers of structure simultaneously:

• audio signal structure  
• symbolic composition structure  
• synthesis hardware structure  
• perceptual musical features  
• metadata knowledge graphs  

Helix converts these layers into feature vectors and graphs that can be compared across composers, games, hardware platforms, and eras.

---

# Music Analysis Ontology

Music analysis operates across multiple structural layers.

Chip synthesis layer  
Audio signal layer  
Perceptual feature layer  
Performance event layer  
Score notation layer  
Musicological structure layer  
Metadata knowledge layer  

Each layer contributes information to a unified **track style vector**.

---

# Supported Data Formats

## Chip formats

VGM  
SPC  
NSF  
SID  
2SF  
GSF  
NCSF  
PSF / PSF2  
S98  
DSF  

These formats expose hardware-level synthesis behavior.

---

## Rendered audio

FLAC  
MP3  
AAC  
Vorbis  
Opus  
WMA  

These provide the perceptual audio signal.

---

## Performance representation

MIDI

Represents performance events such as notes, velocities, and timing.

---

## Score / notation representation

MusicXML  
ABC  
LilyPond  

These encode musical notation structure.

---

## Computational musicology representation

Humdrum / Kern

Used for symbolic structural analysis.

---

# Feature Extraction Layers

Music analysis combines signal processing and musicology.

Key extracted features include:

spectrograms  
mel spectrograms  
MFCC feature vectors  
chroma vectors  
spectral centroid  
spectral brightness  
rhythmic onset density  
loudness curves  

These approximate perceptual features of music.

---

# Synthesis Architecture Analysis

Chip music exposes the underlying synthesis architecture.

Helix extracts synthesis features such as:

FM operator graphs  
operator modulation topology  
feedback loops  
PSG waveform usage  
noise channel behavior  
sample playback structure  

These structures can be modeled as oscillator networks.

FM patches can therefore be interpreted as dynamical systems.

---

# Analysis Pipeline

The Music Substrate pipeline follows a fixed structure.

1 library ingestion
2 chip register parsing
3 synthesis architecture analysis
4 symbolic music extraction
5 computational musicology analysis
6 MIR audio analysis
7 feature synthesis
8 style-space embedding
9 knowledge graph integration
10 LLM interpretation

Stages 3–5 and 9–10 are implemented in `substrates/music/pipeline.py` as direct chip analysis paths.
Stages 6–8 delegate to `labs/music_lab/master_pipeline.py`.

All HIL orchestration goes through `core/hil/interpreter.run_command()`.

---

# External Tag Priority

Chip-format files (VGM, VGZ, SPC, NSF, etc.) read metadata from APEv2 `.tag` sidecar files first.
Internal Mutagen tags are used only as fallback when no sidecar exists.

This enables custom fields not present in internal chip headers:

    Sound chip
    Platform
    Franchise
    Sound Team
    Featuring

Sidecar files follow the naming convention: `filename.ext.tag`

---

# Corpus Analysis: Sonic 3 & Knuckles

Full 10-stage analysis of the S3K soundtrack (104 VGZ tracks).

| Artifact | Contents |
|----------|----------|
| `artifacts/music/track_index.json` | 58 tracks, title/artist/platform/chip |
| `artifacts/music/synthesis_profiles.json` | FM chip feature vectors (stage 3) |
| `artifacts/music/symbolic_representations.json` | Note event reconstructions (stage 4) |
| `artifacts/music/musicology_features.json` | Key, tempo, mode, motif density (stage 5) |
| `artifacts/music/mir_features.json` | Theory + chip combined MIR (104 tracks) |
| `artifacts/music/track_style_vectors.json` | 64-dim feature vectors (stage 7) |
| `artifacts/music/style_space_embedding.json` | PCA 2D projection |
| `artifacts/music/timbre_clusters.json` | K-means k=5 timbre clusters |
| `artifacts/music/analysis_report.md` | Stage 10 — composer fingerprints, synthesis architecture |

HIL verification commands:

    ENTITY list namespace=music                          → 98,310 entities
    ENTITY get music.track:angel_island_zone_act_1       → Angel Island Zone Act 1
    GRAPH neighbors music.composer:jun_senoue            → 4 neighbors
    GRAPH neighbors music.sound_chip:ym2612              → 1 neighbor (sonic_3_knuckles game)  

---

# External Metadata Sources

Music metadata is enriched using external knowledge bases.

Wikidata  
Wikipedia  
MusicBrainz  
VGMDB  
VGMPF  
VGMRips Wiki  
Last.fm  
Spotify  

These sources help identify composers, releases, and relationships.

---

# Integration With Helix Core

Music entities integrate into the Helix entity system.

Examples:

Composer  
Track  
Game  
Platform  
SoundChip  

These entities connect through the Helix knowledge graph.

Example relationships:

composer → composed → track  
track → appears_in → game  
game → runs_on → platform  

---

# Purpose

The Music Substrate transforms music libraries into structured datasets that can be studied computationally.

These datasets allow Helix to analyze:

composer style evolution  
hardware synthesis design  
genre formation  
cross-game musical influence  

Music therefore becomes a structural dataset rather than only an artistic medium.