# HELIX MUSIC SUBSTRATE

The Music Substrate is the Helix environment responsible for analyzing music as a structured system.

Music combines multiple layers of structure simultaneously:

• audio signal structure  
• symbolic composition structure  
• synthesis hardware structure  
• perceptual musical features  
• metadata knowledge graphs  

Helix converts these layers into feature vectors and graphs that can be compared across composers, games, hardware platforms, and eras.

The Music Substrate therefore acts as a **translation system** that converts raw music files into structured computational representations that Helix can reason about.

Music artifacts are progressively transformed into:

raw files  
→ decoded representations  
→ extracted features  
→ fused style vectors  
→ embeddings and clusters  
→ Atlas knowledge graph entities

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

These layers are intentionally redundant.

Different file formats expose different subsets of these layers.

Helix merges all available layers into a unified representation.

---

# Supported Data Formats

The Music Substrate accepts multiple representations of music.

Different formats expose different structural depths.

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

These formats expose **hardware-level synthesis behavior**.

They allow direct reconstruction of sound chip activity.

Helix can extract:

• register writes  
• timing events  
• channel activity  
• patch changes  
• sample triggers  
• voice allocation  

These formats therefore allow **causal reconstruction of synthesis architecture**.

---

## Rendered audio

FLAC  
MP3  
AAC  
Vorbis  
Opus  
WMA  
WAV  

These formats contain only the final audio waveform.

Helix analyzes them using **MIR signal processing techniques**.

Although synthesis architecture is not directly observable, many structural features can still be inferred.

---

## Performance representation

MIDI

Represents performance events such as:

• notes  
• velocities  
• channels  
• timing  

This allows symbolic reconstruction of composition structure.

---

## Score / notation representation

MusicXML  
ABC  
LilyPond  

These encode **written musical notation**.

They provide explicit information about:

• phrasing  
• harmony  
• meter  
• articulation  

---

## Computational musicology representation

Humdrum / Kern

Used for symbolic structural analysis.

These formats allow deeper musicological reasoning such as:

• motif recurrence  
• phrase segmentation  
• harmonic rhythm  

---

# Library Ingestion Layer

Before analysis begins, Helix maintains a persistent **music library index**.

This prevents repeated parsing and allows tracks to be mapped to stable entities.

Each music file is indexed with:

• absolute filesystem path  
• file hash / checksum  
• detected format  
• metadata tags  
• inferred artist / album / title  
• analysis status  

Helix therefore maintains a persistent **music corpus registry**.

Multiple files may map to the same conceptual work.

Example:

```
Angel Island Zone.vgz
Angel Island Zone.flac
Angel Island Zone.mp3
```

All may resolve to the same **music.track entity**.

---

# Metadata Normalization

Metadata is gathered from:

internal file tags  
APEv2 sidecar tags  
external metadata databases  

These are normalized into stable Helix entities.

Primary music entities include:

music.track  
music.album  
music.composer  
music.game  
music.platform  
music.sound_chip  

Identity resolution attempts to unify duplicate records across formats.

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

All formats capable of producing audio signals can pass through this layer.

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

For rendered audio formats, Helix attempts **timbral inference** rather than direct chip reconstruction.

---

# Symbolic Music Reconstruction

Where symbolic information exists (MIDI, chip events, or notation), Helix reconstructs musical structure.

This may include:

note events  
durations  
tempo maps  
meter  
instrument channels  

These symbolic representations feed into later musicology analysis.

---

# Computational Musicology Analysis

Musicological features extracted include:

key estimation  
mode detection  
harmonic rhythm  
motif density  
melodic contour  
rhythmic complexity  
phrase segmentation  

These features describe the compositional structure of a track.

---

# MIR Signal Analysis

All music capable of waveform rendering passes through a MIR feature layer.

Extracted MIR features include:

MFCC vectors  
chroma features  
spectral centroid  
spectral flux  
tempo  
beat structure  
loudness envelopes  

This allows comparison between chip music and rendered audio.

---

# Feature Synthesis

All extracted representations are fused into a unified feature vector.

Each track produces a **TrackStyleVector**.

This vector incorporates:

• synthesis architecture  
• symbolic music structure  
• MIR signal features  
• metadata attributes  

This allows Helix to compare tracks even when they originate from different formats.

---

# Style-Space Embedding

Track style vectors are embedded into a latent style space.

This enables:

nearest-neighbor similarity  
composer clustering  
hardware timbre clustering  
era/style evolution analysis  

Embedding models may include:

PCA  
UMAP  
neural embeddings  

---

# Knowledge Graph Integration

Analysis results are written into the Helix knowledge graph.

Entities created include:

music.track  
music.composer  
music.album  
music.game  
music.platform  
music.sound_chip  

Relationships include:

composer → composed → track  
track → appears_in → game  
game → runs_on → platform  
track → uses_chip → sound_chip  

Analysis artifacts are also linked to entities.

Examples:

track → has_style_vector  
track → belongs_to_timbre_cluster  
composer → associated_with_style_region  

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

Stages 3–5 and 9–10 are implemented in:

```
substrates/music/pipeline.py
```

Stages 6–8 delegate to:

```
labs/music_lab/master_pipeline.py
```

All HIL orchestration goes through:

```
core/hil/interpreter.run_command()
```

---

# External Tag Priority

Chip-format files (VGM, VGZ, SPC, NSF, etc.) read metadata from APEv2 `.tag` sidecar files first.

Internal Mutagen tags are used only as fallback when no sidecar exists.

This enables custom fields not present in internal chip headers:

Sound chip  
Platform  
Franchise  
Sound team  
Featuring  

Sidecar files follow the naming convention:

```
filename.ext.tag
```

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

```
ENTITY list namespace=music
ENTITY get music.track:angel_island_zone_act_1
GRAPH neighbors music.composer:jun_senoue
GRAPH neighbors music.sound_chip:ym2612
```

---

# External Metadata Sources

Music metadata is enriched using external knowledge bases.

Runtime APIs:

MusicBrainz  
Last.fm  
Spotify  

Reference ingestion:

Wikidata  
Wikipedia  
VGMDB  
VGMPF  
VGMRips Wiki  

These sources help identify composers, releases, and relationships.

---

# Integration With Helix Core

Music entities integrate into the Helix entity system.

Examples:

Composer  
Track  
Game  
Platform  
Sound chip  

These entities connect through the Helix knowledge graph.

---

# Purpose

The Music Substrate transforms music libraries into structured datasets that can be studied computationally.

These datasets allow Helix to analyze:

composer style evolution  
hardware synthesis design  
genre formation  
cross-game musical influence  

Music therefore becomes a structural dataset rather than only an artistic medium.