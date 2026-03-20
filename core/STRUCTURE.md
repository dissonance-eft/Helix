# HELIX STRUCTURAL CONTRACT (LAWS)

## 1. SYSTEM BOUNDARIES
- **Library ≠ Atlas**: The Library contains reference models (priors). The Atlas contains research memory (posteriors).
- **Generalizable → Library**: Universal rules, hardware specifications, and axiomatic models go to the Library.
- **Specific → Atlas**: Measurements, instances, and analysis results go to the Atlas.

## 2. EXECUTION PIPELINE
- **Library → Helix → Atlas**: Helix processes inputs by mapping them against Library references and compiling results into the Atlas.
- **No Direct Atlas Writes**: All knowledge must pass through the Helix pipeline and be compiled by the Atlas Compiler.

## 3. CCS REQUIREMENT
- **All Atlas Entities Require CCS**: Any entity committed to the Atlas must include a 6-axis Cognitive Coordinate System (CCS) embedding.
- **Validity Threshold**: Embeddings lacking 6 axes or having confidence < 0.30 are systematically invalid/unreliable.

## 4. SCHEMA UNIFICATION
- **Single Canonical Schema**: Both Library and Atlas entities must conform to the unified schema defined in the system SPEC.
- **Colon-Separated Identity**: Every entry must use the `<domain>.<type>:<slug>` ID format.
- **Structured Evidence**: Loose evidence arrays are prohibited; all evidence must use the formal structured schema.
