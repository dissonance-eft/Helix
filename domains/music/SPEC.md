# HELIX MUSIC SUBSTRATE SPECIFICATION

**Version:** 2.2
**Status:** Authoritative target specification — implementation status tracked in README.md §11
**Relationship:** Extends `domains/music/README.md`

---

## 1. DOMAIN SCOPE

The Music Substrate operates across three observability layers:
- **Causal**: Hardware synthesis logic (register writes, chip state)
- **Symbolic**: Compositional intent (MIDI, score notation)
- **Perceptual**: Psychoacoustic outcome (rendered audio, MIR features)

Its goal is to extract structural invariants that survive across these layers when format, hardware, or era changes.

---

## 2. DOMAIN-LOCAL STRUCTURAL SIGNALS

These signals are extracted by the music pipeline and are domain-local. They are NOT the same as HelixEmbedding axes. They feed into the feature fusion stage, which then produces a `MusicStyleVector` that is projected into the shared embedding.

### 2.1 Causal Signals (Hardware/Driver)
- **`register_write_density`**: Chip register writes per second
- **`operator_topology_complexity`**: Graph complexity of FM synthesis algorithms
- **`driver_tick_jitter`**: Temporal variance in command dispatch
- **`lfsr_noise_entropy`**: Entropy of noise channel bitstreams

### 2.2 Symbolic Signals (Compositional)
- **`interval_entropy`**: Shannon entropy of melodic intervals
- **`rhythmic_quantization_error`**: Deviation from absolute grid centers
- **`harmonic_vocab_size`**: Number of unique chord types used
- **`phrase_recurrence_ratio`**: Percentage of phrases that repeat ≥ 90% similarity

### 2.3 Perceptual Signals (Audio / MIR)
- **`spectral_centroid_drift`**: Variance in spectral brightness over time
- **`onset_density`**: Perceived rhythmic events per second
- **`timbre_cluster_count`**: Number of distinct MFCC clusters detected

---

## 3. SHARED EMBEDDING PROJECTION

Music-domain signals are fused into a `MusicStyleVector` and projected into the shared `HelixEmbedding` format via Stage 9.

**Projection mapping** (signal → embedding axis):

| HelixEmbedding Axis | Primary Music Signal | Normalization Method |
|---------------------|----------------------|----------------------|
| `structure` | `phrase_recurrence_ratio` | Domain baseline: VGM loop-density |
| `complexity` | `rhythmic_quantization_error` | Inverse of deviation from grid |
| `repetition` | `hierarchical_motif_depth` | Normalized count of nested repeats |
| `density` | `register_write_density` | Log-normalized per-chip event rate |
| `variation` | `interval_entropy` | Percentile of composer-specific variance |
| `expression` | `spectral_transition_slope` | Sigmoid-mapped slope of timbral shifts |

**Non-equivalence rule**: The embedding axis names (`structure`, `complexity`, etc.) are shared system-wide. The music signal names are domain-local. The mapping above is explicit and should not be treated as naming equivalence.

**Projection schema versioning**: A `projection_schema` field should be stamped on all music embedding artifacts to enable comparison across schema versions. (Not yet implemented — see §4 status.)

---

## 4. PIPELINE STAGES

| Stage | Responsibility | Input | Output | Status |
|-------|----------------|-------|--------|--------|
| 1 | Ingestion | Source path | Library index entry | ✅ |
| 2 | Decoding | VGM/FLAC/MIDI | ControlSequence / Audio / SymbolicScore | ✅ |
| 3 | Static parse | Header data | Metadata artifact | ✅ |
| 4 | Causal trace | Register log | Timeline trace artifact | ✅ |
| 5 | Symbolic extraction | Event stream | SymbolicScore artifact | ✅ |
| 6 | MIR analysis | Rendered audio | SignalProfile artifact | ✅ |
| 7 | Motif detection | Phrasal data | Motif entity candidates | ✅ |
| 8 | Feature fusion | All artifacts | MusicStyleVector | ✅ |
| 9 | HelixEmbedding projection | MusicStyleVector | HelixEmbedding artifact | ⚠️ Partial |
| 10 | Atlas compilation | All artifacts | Atlas entities | ⚠️ Partial |

---

## 5. ARTIFACT SCHEMAS

### ControlSequence (`artifacts/music/<id>/control_seq.json`)
```json
{
  "track_id": "...",
  "chip_target": "YM2612",
  "events": [...],
  "timing_vblank": true
}
```

### SymbolicScore (`artifacts/music/<id>/symbolic.json`)
```json
{
  "track_id": "...",
  "notes": [...],
  "interval_histogram": {}
}
```

### SignalProfile (`artifacts/music/<id>/signal.json`)
```json
{
  "track_id": "...",
  "spectral_centroid": 2800.3,
  "onset_density": 4.2
}
```

### HelixEmbedding (`artifacts/music/<id>/embedding.json`)
```json
{
  "complexity": 0.71,
  "structure": 0.88,
  "repetition": 0.64,
  "density": 0.53,
  "expression": 0.41,
  "variation": 0.37,
  "confidence": 0.72,
  "domain": "music",
  "source_vector": "music_style_vector",
  "projection_schema": "music_v1"
}
```

---

## 6. VALIDATION RULES

- **Deterministic check**: Re-running the pipeline on a fixed source hash must produce identical HelixEmbedding coordinates
- **Cross-layer alignment**: Symbolic score durations must match perceptual waveform durations within 5ms
- **Library reference compliance**: Any chip-level measurement must be validated against `codex/library/audio/chips/` specifications
- **Null model guard**: A null corpus (randomized register-write sequences) must not produce embedding confidence above floor — not yet implemented

---

## 7. METRIC SPACE / SIMILARITY / DISTANCE

The HelixEmbedding metric space uses Euclidean distance normalized by √6:

```
distance(a, b) = euclidean(a, b) / sqrt(6)          ∈ [0, 1]
similarity(a, b) = 1 - distance(a, b)               ∈ [0, 1]
```

**Triangle inequality** applies to **distance**, not similarity:
```
d(a, c) ≤ d(a, b) + d(b, c)
```

A violation is a `STRUCTURAL_FAILURE` and must be flagged before Atlas promotion.

---

## 8. ENTRY / HSL INTEGRATION STATE

**Target**: HSL commands `INGEST_TRACK music.<id>`, `ANALYZE_TRACK music.<id>`\
**Current**: Operators partially dispatch to music adapters. Full end-to-end HSL path not complete.

---

## 9. THRESHOLDS AND CALIBRATION

| Threshold | Value | Status |
|-----------|-------|--------|
| Minimum embedding confidence | 0.30 | Provisional — global default, not music-calibrated |
| Cross-layer alignment tolerance | 5ms | Defined; calibration basis unknown |
| Phrase recurrence similarity floor | 90% | Defined; not validated against null music corpus |

Calibration procedure for confidence floor: establish null corpus → compute embedding distribution → set at `mean + 2 * std`. Not yet performed for music domain.

---

## 10. PROMOTION CONDITIONS

Invariant candidates must pass the global 6-criterion promotion gate (see `docs/GOVERNANCE.md`):
1. Reproducibility (≥ 2 independent runs)
2. Multi-domain observation (≥ 2 domains)
3. Minimum confidence ≥ threshold
4. Pass rate ≥ 80%
5. Signal above minimum threshold
6. Latest probe version used

---

## 11. KNOWN ASSUMPTIONS / OPEN CONSTRAINTS

- Music substrate ingests all audio codecs equally via the adapter layer — VGM, SPC, PSF/PSF2/2SF/DSF/GSF/NCSF/USF, S98, AAC, MP2, MP3, Opus, Vorbis, WMA, and others. No format is primary; the decoding adapter abstracts codec differences from the pipeline. New formats are added as adapters, not as pipeline changes.
- Chip-level measurements assume library chip specifications are accurate
- Cross-format alignment assumes 5ms tolerance is sufficient for invariant preservation
- `projection_schema` versioning for music embeddings not yet implemented — risk of silent comparability loss across schema changes
