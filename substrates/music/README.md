# HELIX MUSIC SUBSTRATE SPECIFICATION

Version: 1.0-draft  
Status: Canonical substrate specification  
Authority: This document is the implementation contract for the Helix Music Substrate.  
Purpose: Prevent architectural drift, duplicate scripts, misplaced functionality, and hallucinated scope.

---

# 0. WHY THIS DOCUMENT EXISTS

This document is not a casual README.

It is the **formal design specification** for the Helix Music Substrate.

Its purpose is to make the Music Substrate as self-reconstructing as possible in concept, so that:

- an LLM can rebuild the substrate without inventing architecture
- existing scripts are not duplicated under new names
- responsibilities are not placed into the wrong repo or module
- future planned components are implemented with the same structural DNA
- Helix remains what it is, rather than slowly mutating into a pile of unrelated music scripts

If code conflicts with this document, this document takes precedence until intentionally revised.

This specification is intentionally explicit and partially redundant.

Redundancy is a feature, not a bug.

---

# 1. SUBSTRATE IDENTITY

## 1.1 What the Music Substrate is

The Music Substrate is the Helix environment responsible for transforming music libraries into structured computational datasets.

It analyzes music as a layered structural system spanning:

- synthesis mechanisms
- audio perception
- symbolic composition
- metadata identity
- graph relationships

It converts music artifacts into:

raw files  
→ decoded representations  
→ feature layers  
→ fused style vectors  
→ embeddings and clusters  
→ Atlas entities and graph edges

The Music Substrate is therefore a **translation and extraction layer**.

It is responsible for turning music into structured data that Helix can reason over.

## 1.2 What the Music Substrate is not

The Music Substrate is not:

- a DAW
- a player UI
- a generic music streaming app
- an all-purpose tag editor
- a pure MIR-only toolkit
- a pure symbolic musicology toolkit
- a pure VGM utility pack
- a dumping ground for unrelated game-audio experiments

The substrate does not exist to “do anything music-related.”

It exists to convert music into structured, comparable Helix representations.

## 1.3 Core identity statement

The Music Substrate studies both:

- how sound is generated
- how sound is perceived

and links both to:

- compositional structure
- metadata identity
- graph-level knowledge

This is the defining DNA of the substrate.

Any implementation that loses one of these layers is incomplete.

---

# 2. POSITION WITHIN HELIX

## 2.1 Helix responsibility split

Helix is divided into four major responsibility layers:

### Core
Execution system, HIL, entities, graph infrastructure, validators, integrity rules.

### Substrates
Domain-specific ingestion and structural analysis.

### Labs
Exploratory and experimental modeling built on top of substrate outputs.

### Atlas
Persistent structured knowledge and research memory.

## 2.2 Music Substrate responsibility

The Music Substrate is responsible for:

- file ingestion
- metadata normalization
- format routing
- chip/event parsing
- waveform analysis
- symbolic reconstruction
- musicological extraction
- feature fusion
- artifact generation
- Atlas entity/relationship updates

## 2.3 Music Lab responsibility

Music Lab is responsible for higher-level exploration and experimentation using substrate outputs.

This includes:

- clustering experiments
- comparative style-space studies
- composer attribution experiments
- longitudinal corpus experiments
- embedding experiments
- diagnostic visualizations
- research scripts that consume substrate artifacts

## 2.4 Boundary rule

If a component is required for deterministic ingestion and canonical artifact production, it belongs in the Music Substrate.

If a component is exploratory, comparative, experimental, or replaceable without changing the canonical substrate outputs, it belongs in Music Lab.

This boundary must be preserved.

---

# 3. MUSIC SUBSTRATE ONTOLOGY

The Music Substrate operates across multiple structural layers.

These layers are independent but partially overlapping.

## 3.1 Structural layers

### Chip synthesis layer
The hardware/control layer for chip-native formats.

### Audio signal layer
The rendered waveform layer.

### Perceptual feature layer
Human-facing signal features extracted from audio.

### Performance event layer
Event representations such as note timing and velocity.

### Score notation layer
Explicit notation structure.

### Musicological structure layer
Higher-order composition features such as harmony, motif, and phrasing.

### Metadata knowledge layer
Identity, authorship, release, game/platform, and external source relationships.

## 3.2 Redundancy principle

Different formats expose different subsets of these layers.

The substrate must merge all available layers rather than assuming one canonical representation.

This is a hard design rule.

---

# 4. SUPPORTED INPUT MODES

The Music Substrate supports multiple music representations.

Each representation grants different structural depth.

## 4.1 Chip/event-native formats

Supported formats include:

- VGM
- VGZ
- SPC
- NSF
- SID
- 2SF
- GSF
- NCSF
- PSF / PSF2
- S98
- DSF

These formats expose causal control information.

Where possible, they allow extraction of:

- register writes
- timing events
- voice allocation
- patch configuration
- algorithm changes
- operator states
- sample triggers

These are the deepest formats for causal synthesis analysis.

## 4.2 Rendered audio formats

Supported formats include:

- FLAC
- MP3
- AAC
- Vorbis
- Opus
- WMA
- WAV

These formats expose the final audio waveform only.

They support:

- MIR extraction
- perceptual feature analysis
- segmentation
- timbral modeling
- comparative audio analysis

They do not directly expose causal synthesis structure.

## 4.3 Performance formats

Supported formats include:

- MIDI

These expose note and timing events.

They support:

- symbolic reconstruction
- phrase and tempo analysis
- note-density analysis
- performance event analysis

## 4.4 Score / notation formats

Supported formats include:

- MusicXML
- ABC
- LilyPond

These support explicit notation-based analysis.

## 4.5 Computational musicology formats

Supported formats include:

- Humdrum / Kern

These support deeper symbolic and structural reasoning.

## 4.6 Capability ladder rule

The Music Substrate must use the deepest available representation.

Priority:

1. chip/event-native causal data
2. symbolic/performance data
3. rendered audio data
4. metadata-only fallback

If multiple representations exist for the same work, Helix should merge them.

---

# 5. LIBRARY AND CORPUS MODEL

## 5.1 Persistent music library index

The Music Substrate must maintain a persistent music library index.

Purpose:

- avoid repeated blind rescans
- map local files to stable conceptual entities
- preserve provenance
- track analysis status

Each indexed file stores:

- absolute file path
- relative corpus path if applicable
- file hash
- detected format
- file size
- metadata source availability
- analysis status by stage
- last analyzed timestamp
- linked entity candidate(s)

## 5.2 Conceptual-work model

Multiple file representations may map to one conceptual work.

Example:

- Angel Island Zone.vgz
- Angel Island Zone.flac
- Angel Island Zone.mp3
- Angel Island Zone.mid

may all map to:

music.track:angel_island_zone_act_1

This is a core rule.

The substrate must distinguish between:

- file instance
- representation type
- conceptual track entity

## 5.3 Local-library-first rule

The local library is the corpus anchor.

External metadata may enrich local entities, but should not bloat the graph with unrelated objects that are not relevant to the local corpus unless explicitly allowed by the spec.

---

# 6. METADATA NORMALIZATION

## 6.1 Metadata sources

Metadata may be gathered from:

- internal file tags
- APEv2 sidecar tags
- local library databases
- external metadata APIs
- curated reference datasets

## 6.2 Canonical music entity types

Primary music entity types include:

- music.track
- music.album
- music.composer
- music.game
- music.platform
- music.sound_chip
- music.sound_team
- music.dataset
- music.instrument
- music.sound_driver

Not all must exist immediately, but these are canonical planned types.

## 6.3 Identity resolution goals

Metadata normalization must attempt to unify records across:

- multiple file formats
- alternate dumps
- re-encodes
- remasters
- soundtrack albums
- game-native versions
- external metadata sources

## 6.4 External metadata classes

### Runtime APIs
Dynamic or queryable enrichment sources.

Examples:
- MusicBrainz
- Last.fm
- Spotify

### Reference ingestion sources
Stable or archival sources used to seed Atlas.

Examples:
- Wikidata
- Wikipedia
- VGMDB
- VGMPF
- VGMRips Wiki

## 6.5 External tag priority for chip formats

Chip-native formats must prioritize APEv2 `.tag` sidecar files first.

Mutagen or internal tags are fallback only.

Reason:
chip-sidecar metadata can contain fields that are absent from embedded headers.

Supported sidecar fields include:

- Sound chip
- Platform
- Franchise
- Sound team
- Featuring

Naming convention:

filename.ext.tag

---

# 7. DUAL TIMELINE MODEL

Chip-native music exposes two different timelines.

The substrate must treat them separately.

## 7.1 Causal timeline

The causal timeline represents the control instructions that generate the sound.

Examples include:

- register writes
- operator parameter changes
- algorithm switches
- voice allocation
- sample triggers
- envelope phase transitions

Example:

t=0.00 channel1 key_on  
t=0.02 operator3 attack  
t=0.05 algorithm switch  
t=0.20 feedback increase  
t=0.50 key_off

This timeline describes how the synthesizer is driven.

## 7.2 Perceptual timeline

The perceptual timeline represents the listener-facing sound result.

Examples include:

- spectral centroid
- loudness envelope
- harmonic density
- onset transients
- timbral shifts

Example:

0.00 attack transient  
0.10 brightness spike  
0.25 harmonic saturation  
0.50 decay

This timeline describes how the music is perceived.

## 7.3 Cause–effect mapping

Helix must preserve the relationship between these two timelines.

Examples:

- register write → spectral centroid shift
- algorithm change → timbre cluster change
- envelope change → amplitude contour change

This is a defining feature of the Music Substrate.

Traditional MIR-only systems do not preserve this distinction.

Helix must.

## 7.4 Missing causal data behavior

If a format lacks chip/event-level information, the causal timeline is null.

This is acceptable.

Audio-only tracks still remain valid substrate objects.

The system must gracefully degrade rather than fail.

---

# 8. FEATURE LAYERS

The Music Substrate extracts multiple feature families.

## 8.1 MIR features

Examples include:

- spectrogram
- mel spectrogram
- MFCC vectors
- chroma features
- spectral centroid
- spectral flux
- loudness curves
- onset density
- tempo estimation

## 8.2 Symbolic features

Examples include:

- note events
- durations
- tempo maps
- time signatures
- instrument/channel assignment
- phrase candidates

## 8.3 Musicology features

Examples include:

- key estimation
- mode detection
- harmonic rhythm
- motif density
- melodic contour
- rhythmic complexity
- phrase segmentation

## 8.4 Synthesis features

Examples include:

- FM operator graphs
- modulation topology
- feedback usage
- PSG waveform usage
- noise channel density
- sample trigger rates
- patch structure
- channel allocation profiles

## 8.5 Metadata features

Examples include:

- release year
- franchise
- soundtrack context
- composer team
- platform
- chip family

---

# 9. FEATURE FUSION

All available feature layers must be fused into a unified track representation.

This is the TrackStyleVector.

The TrackStyleVector is the substrate’s canonical per-track representation.

It is the bridge between:

- chip synthesis
- symbolic composition
- perceptual signal analysis
- metadata context

This fused representation is what later supports:

- style-space embeddings
- clustering
- composer similarity
- cross-platform comparison
- Atlas enrichment

---

# 10. TRACKSTYLEVECTOR SCHEMA

Every analyzed track produces a TrackStyleVector.

Canonical schema:

TrackStyleVector
{
    track_id: string
    title: string
    composer: string
    platform: string
    sound_chip: string

    synthesis_features:
    {
        fm_algorithm_distribution: array[8]
        operator_feedback_mean: float
        operator_ratio_entropy: float
        psg_waveform_usage: array
        noise_channel_density: float
        sample_trigger_rate: float
    }

    symbolic_features:
    {
        tempo_bpm: float
        key_estimate: string
        mode: string
        note_density: float
        melodic_interval_entropy: float
        chord_change_rate: float
        motif_repetition_score: float
    }

    mir_features:
    {
        spectral_centroid_mean: float
        spectral_flux_mean: float
        chroma_vector: array[12]
        mfcc_mean: array[13]
        loudness_dynamic_range: float
        onset_density: float
    }

    structural_features:
    {
        phrase_length_mean: float
        rhythmic_complexity: float
        harmonic_rhythm: float
    }

    metadata_features:
    {
        release_year: int
        game_franchise: string
        composer_team: string
    }
}

This schema is binding unless revised.

---

# 11. OTHER CANONICAL SCHEMAS

## 11.1 TrackIndex

TrackIndex
{
    track_id: string
    title: string
    composer: string
    album: string
    game: string
    platform: string
    sound_chip: string
    file_path: string
    source_format: string
}

## 11.2 SynthesisProfile

SynthesisProfile
{
    track_id: string
    chip: string

    operator_graphs: list
    algorithm_usage: array
    feedback_levels: array

    channel_usage:
    {
        fm_channels_active: int
        psg_channels_active: int
        noise_channel_usage: float
    }

    patch_reuse_score: float
}

## 11.3 SymbolicRepresentation

SymbolicRepresentation
{
    track_id: string

    note_events:
        list(note, start_time, duration, velocity)

    tempo_map:
        list(time, tempo)

    time_signature_map:
        list(time, signature)

    instrument_channels:
        list(channel_id, instrument_type)
}

## 11.4 MIRFeatures

MIRFeatures
{
    track_id: string

    mfcc_mean: array[13]
    mfcc_variance: array[13]

    chroma_mean: array[12]

    spectral_centroid_mean: float
    spectral_bandwidth_mean: float
    spectral_flux_mean: float

    tempo_estimate: float
    onset_rate: float
    loudness_dynamic_range: float
}

## 11.5 StyleEmbedding

StyleEmbedding
{
    track_id: string

    vector: array[64]

    pca_projection:
    {
        x: float
        y: float
    }

    cluster_id: int
}

---

# 12. PIPELINE CONTRACT

The Music Substrate pipeline is deterministic and stage-based.

Canonical stage order:

1. library ingestion
2. chip register parsing
3. synthesis architecture analysis
4. symbolic music extraction
5. computational musicology analysis
6. MIR audio analysis
7. feature synthesis
8. style-space embedding
9. knowledge graph integration
10. LLM interpretation

No stage may silently change meaning without updating this specification.

---

# 13. IMPLEMENTATION OWNERSHIP

This section exists to prevent duplicate scripts and confused placement.

## 13.1 Substrate-owned modules

These belong in `substrates/music/` because they are required for canonical substrate execution.

### pipeline.py
Top-level substrate orchestrator for the canonical 10-stage pipeline.

### config.py
Music substrate configuration and defaults.

### tag_reader.py
Reads metadata from internal tags and sidecar files.

### vgm_parser.py
Parses chip/event-native files and produces causal event timelines.

### smps_reconstructor.py
Reconstructs symbolic/note-level structure from event streams where applicable.

### channel_profiler.py
Computes channel-level usage metrics.

### patch_fingerprinter.py
Generates patch and timbral fingerprints from causal synthesis data.

### feature_extractor.py
Computes feature layers required by the canonical pipeline.

### measurement_engine.py
Computes structural metrics used by canonical schemas.

### style_signal_generator.py
Converts extracted features into normalized fused style signals.

### knowledge_engine.py
Maps analysis results into Atlas entities and graph relationships.

### generate_chip_report.py
Produces deterministic chip-level analytical reports used by the substrate.

### run_context.py
Defines runtime execution context for substrate runs.

## 13.2 Lab-owned modules

These belong in `labs/music_lab/` because they are higher-order, exploratory, or comparative.

Examples include:

- clustering experiments
- style-space experiments
- alternative embedding methods
- composer attribution experiments
- corpus-level comparative studies
- research notebooks/scripts
- visualization experiments

## 13.3 Boundary rule

If removing the module would break canonical substrate artifact generation, it belongs in the substrate.

If removing the module would only remove an experiment or optional model, it belongs in Music Lab.

---

# 14. REPOSITORY TOPOLOGY CONTRACT

Canonical expected location:

substrates/music/

This directory is the home of the Music Substrate.

The substrate must not place core code into:

- core/
- atlas/
- interface/
- labs/ (unless it is explicitly a lab component)

## 14.1 Expected substrate files

The exact file list may evolve, but the following conceptual roles must exist:

- pipeline orchestrator
- config
- tag reader
- chip parser
- symbolic reconstruction component
- feature extraction component
- measurement component
- patch/synthesis analysis component
- knowledge graph export component
- runtime context component
- README/specification

Even if filenames change later, these roles must remain represented.

---

# 15. ARTIFACT CONTRACT

Artifacts are deterministic outputs of canonical substrate runs.

Artifacts are not the final knowledge layer.

Artifacts are stored under:

artifacts/music/

Required outputs:

- track_index.json
- synthesis_profiles.json
- symbolic_representations.json
- musicology_features.json
- mir_features.json
- track_style_vectors.json
- style_space_embedding.json
- timbre_clusters.json
- analysis_report.md

These correspond to stages 3–10.

## 15.1 Artifact rule

Artifacts are reproducible run outputs.

Atlas is the persistent normalized knowledge layer.

This distinction must not blur.

---

# 16. DETERMINISM REQUIREMENT

Given identical inputs and identical config, the Music Substrate must produce identical artifact structures.

Any randomized algorithm must use fixed seeds.

Any nondeterministic external dependency must be normalized or isolated.

Reproducibility is mandatory.

---

# 17. ATLAS MAPPING CONTRACT

Artifacts must update Atlas entities and graph relationships.

Examples of music entities:

- music.track:angel_island_zone_act_1
- music.composer:jun_senoue
- music.album:sonic_3_and_knuckles
- music.game:sonic_3_and_knuckles
- music.platform:sega_genesis
- music.sound_chip:ym2612

Examples of relationships:

- composer → composed → track
- track → appears_in → game
- game → runs_on → platform
- track → uses_chip → sound_chip

Examples of derived property attachments:

- track → has_style_vector
- track → belongs_to_timbre_cluster
- composer → associated_with_style_region

---

# 18. CONFIGURATION CONTRACT

The substrate must define explicit config defaults.

At minimum, configuration must control:

- supported formats
- style vector dimensionality
- clustering parameters
- random seed
- metadata source priorities
- output paths
- runtime toggles for optional stages

These defaults must be documented and stable.

Silent config drift is forbidden.

---

# 19. HIL CONTRACT

All automated orchestration occurs through HIL via Helix Core.

Examples:

SUBSTRATE run music soundtrack:"Sonic 3 & Knuckles"  
ENTITY get music.track:angel_island_zone_act_1  
GRAPH neighbors music.composer:jun_senoue

The substrate must not invent an alternative orchestration language.

HIL is the only official automation interface.

---

# 20. PLANNED COMPONENTS

The following are part of the intended long-term DNA of the Music Substrate even if not fully implemented yet.

## 20.1 Full local music corpus ingestion
Support large personal libraries across chip formats, symbolic formats, and rendered audio.

## 20.2 Rich entity seeding from local library + reference databases
Local-first seeding with enrichment from reference sources.

## 20.3 Causal/perceptual comparative modeling
Direct study of synthesis mechanisms versus perceived outcomes.

## 20.4 Cross-format track unification
Mapping the same conceptual track across VGM, FLAC, MP3, MIDI, and other forms.

## 20.5 Style-space and composer fingerprinting
Corpus-level style mapping across composers, hardware, and eras.

## 20.6 Multi-chip and multi-platform synthesis evolution studies
Longitudinal structural analysis of hardware sound design.

These are planned components and must be treated as part of the same system lineage.

Future implementations should extend this DNA, not replace it.

---

# 21. ANTI-DRIFT RULES

The following rules exist to stop LLM hallucination and repo mutation.

## 21.1 No duplicate script rule
Do not create a new script if an existing script already owns that responsibility.

Instead:
- extend the existing script
- refactor it intentionally
- document the change in the spec

## 21.2 No misplaced responsibility rule
Do not place substrate logic in Music Lab.
Do not place lab logic in the substrate.
Do not place domain-specific logic in Helix Core.

## 21.3 No silent renaming rule
Do not rename core concepts casually.

Examples of concepts that must remain stable unless explicitly changed in the spec:
- TrackStyleVector
- causal timeline
- perceptual timeline
- synthesis profile
- knowledge graph integration

## 21.4 No speculative expansion rule
Do not add unrelated music tooling just because it sounds useful.

Every addition must answer:
How does this help convert music into structured Helix representations?

## 21.5 No architecture invention rule
If a behavior is not defined, extend this document rather than improvising hidden architecture.

---

# 22. RECONSTRUCTION GOAL

The long-term goal of this specification is that a future LLM could reconstruct the Music Substrate from this document alone with minimal hallucination.

That means this document must continue to grow in explicitness over time.

Prompts are execution aids.

This document is the real source of truth.

---

# 23. PURPOSE

The Music Substrate converts music libraries into structured research datasets.

Helix uses these datasets to analyze:

- composer style evolution
- hardware synthesis design
- genre formation
- cross-game musical influence
- chip-level sound design strategies
- relationships between synthesis causality and musical perception

Music therefore becomes a computational dataset describing both sound synthesis and musical structure.

This is the defining purpose of the substrate.