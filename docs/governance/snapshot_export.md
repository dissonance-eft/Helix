# Snapshot Export

**Version:** 1.0
**Canonical command:** `python scripts/make_snapshot.py`
**Schema:** `snapshot_schema_v1`

---

## What Is a Snapshot

A Helix snapshot is a compact, deterministic zip export of the repository, optimised for LLM context ingestion. It is NOT a backup. It is NOT a deployment artifact. It is a **reconstructible structural export** — everything a model needs to understand the Helix architecture, code, docs, and manifests, without the bulk data it does not need.

The snapshot makes another model feel as close as possible to having read-access to the real repo.

---

## How to Run

```powershell
# Standard snapshot (recommended)
python scripts/make_snapshot.py

# Include bulk library content (larger output)
python scripts/make_snapshot.py --include-library

# Include heavy atlas payloads
python scripts/make_snapshot.py --include-atlas-heavy

# Custom file size limit (default 0.5 MB per file)
python scripts/make_snapshot.py --max-file-mb 1.0

# Custom output path
python scripts/make_snapshot.py --output C:\exports\helix.zip
```

Outputs are written to the repo root:
- `helix_snapshot.zip` — overwrites on each run

---

## What Is Included (Default)

| Category | Included |
|----------|---------|
| All `.py`, `.md`, `.yaml`, `.yml` source | ✅ Full content |
| All `.json`, `.toml`, `.txt`, `.ps1` source | ✅ Full content (under size limit) |
| `docs/` tree (all subfolders) | ✅ Full content |
| Domain `README.md`, `SPEC.md`, `manifest.yaml` | ✅ Full content |
| Application `manifest.yaml`, docs | ✅ Full content |
| `core/` governance, validation, enforcement | ✅ Full content |
| `MANIFEST.yaml` | ✅ Full content |
| `codex/library/` bulk data | ❌ Indexed only |
| `codex/atlas/` heavy payloads | ❌ Indexed only |
| `outputs/` generated artifacts | ❌ Excluded entirely |
| `.git/`, `__pycache__/`, binaries | ❌ Excluded |

Files exceeding the size limit (default 0.5 MB) are indexed rather than included.

---

## What Is Excluded and Why

| Path | Reason | Represented by |
|------|--------|----------------|
| `codex/library/` | Bulk reference data — not needed for structure | Index entry in SNAPSHOT_OMISSIONS.json |
| `codex/atlas/` heavy blobs | Embedding payloads too large | Index entry in SNAPSHOT_OMISSIONS.json |
| `outputs/` | Generated analysis artifacts — transient | Excluded entirely |
| `.git/` | VCS internals | Silently excluded |
| `__pycache__/`, `*.pyc` | Compiled bytecode | Silently excluded |
| Files > size limit | Too large for practical LLM ingestion | Index entry in SNAPSHOT_OMISSIONS.json |
| Binary files (`.png`, `.mp3`, etc.) | Not human/model readable | Index entry |

**Exclusion ≠ invisibility.** Every excluded path appears in `SNAPSHOT_OMISSIONS.json` and `SNAPSHOT_TREE.txt` so a model knows what exists but was not included.

---

## Metadata Files Inside the Zip

| File | Contents |
|------|----------|
| `SNAPSHOT_README.md` | How to interpret the snapshot; key files to read first |
| `SNAPSHOT_MANIFEST.json` | Generated metadata: stats, options, file list, schema version |
| `SNAPSHOT_TREE.txt` | Complete repo tree with FULL / INDEXED / OMITTED markers |
| `SNAPSHOT_OMISSIONS.json` | All excluded paths with sizes and reasons |

---

## How to Upload for External Model Review

1. Run `python scripts/make_snapshot.py`
2. Upload `helix_snapshot_latest.zip` to ChatGPT or equivalent
3. Tell the model: *"Read SNAPSHOT_README.md first, then MANIFEST.yaml, then explore the structure."*

The model should be able to recover the full architectural understanding of Helix from the snapshot without access to the real repo.

---

## Snapshot Schema

`snapshot_schema_v1` — defined in `scripts/make_snapshot.py`. Schema version is stamped in all metadata files. Bump the version constant when inclusion rules, metadata shape, or output format changes.

---

## This Is Not a Backup

- Does not include `.git/` — not suitable for repo restore
- Does not include all binary assets
- Does not include bulk data
- Does not preserve runtime state

For backup, use standard git tooling.

