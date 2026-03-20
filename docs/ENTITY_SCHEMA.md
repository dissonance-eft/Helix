# Helix Entity Schema

## ID Format

All entity IDs use: `domain.type:slug`

| Component | Description | Example |
|-----------|-------------|---------|
| `domain`  | Knowledge domain | `music`, `tech`, `games`, `language`, `math` |
| `type`    | Entity type | `artist`, `track`, `sound_chip`, `invariant` |
| `slug`    | Kebab-case identifier | `yuzo-koshiro`, `ym2612` |

## Core Entity Types (19)

| Type | Domain | Description |
|------|--------|-------------|
| `artist` | music | Composer / performer |
| `track` | music | Individual musical work |
| `album` | music | Collection of tracks |
| `sound_chip` | tech | Hardware synthesis component |
| `platform` | tech | Gaming / computing platform |
| `genre` | music | Musical genre classification |
| `era` | music | Historical time period |
| `motif` | music | Recurring musical pattern |
| `technique` | music | Compositional technique |
| `invariant` | system | Discovered structural law |
| `experiment` | system | Research probe result |
| `style_vector` | music | Computed artist fingerprint |
| `operator_topology` | tech | Chip operator configuration |
| `voice_structure` | music | Channel arrangement |
| `harmonic_pattern` | music | Chord / harmony sequence |
| `rhythmic_pattern` | music | Rhythmic structure |
| `timbre_profile` | music | Spectral characteristics |
| `relationship` | system | Connection between entities |
| `claim` | system | Falsifiable hypothesis |

## Required Fields

Every entity must include:
- `entity_id`: Canonical `domain.type:slug` identifier
- `entity_type`: One of the 19 types above
- `created_at`: ISO 8601 timestamp
- `source`: Origin of the data (e.g., `library`, `analysis`, `inferred`)

## CCS Embedding

All Atlas entities must include a 6-axis Cognitive Coordinate System embedding:
- Complexity, Structure, Repetition, Density, Expression, Variation
- Values: float [0.0, 1.0]
- Minimum confidence threshold: 0.30
