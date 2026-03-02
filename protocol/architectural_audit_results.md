# ARCHITECTURAL AUDIT — HELIX REPOSITORY

## SECTION 1 — Current Topology Map
- **CORE (Ring 0):** `/core/` (Bases, EIP, Irreducibility, Collapse, Registries). [ISOLATED]
- **PROTOCOL (Ring 1):** `/protocol/` (Amendment, Validation, Substrate Resolution). [ACTIVE]
- **RUNTIME (Ring 2):** `/runtime/` (Infrastructure, Hashing, IO, Platform, entry-point `helix.py`). [ACTIVE]
- **SANDBOX (Ring 3):** `/sandbox/` (Experiments, Domain Data, Layers). [SANDBOXED]
- **ARTIFACT:** `/artifacts/`, `/docs/`.

## SECTION 2 — Violations Detected
1. **ONTOLOGY_LEAK (RESOLVED):** Legacy enums and schema were moved from `/sandbox/core_legacy/` to `/core/`.
2. **INFRA_LEAK (RESOLVED):** `substrate_resolution.py` was moved from Protocol to Runtime, then correctly returned to **PROTOCOL** (Ring 1).
3. **EXECUTION_LEAK (RESOLVED):** `helix.py` was moved from Sandbox to **RUNTIME** (Ring 2).
4. **UPWARD_DEPENDENCY (DETECTED):** `runtime/os/` files still use `infra.*` imports. Corrected to `runtime.infra.*`.

## SECTION 3 — Proposed Folder Tree (Clean Architecture)
```text
/core/
    /enums/
    /schema/
    bases.py
    eip.py
    ...
/protocol/
    /tests/
    amendment_protocol.py
    substrate_resolution.py
    validate_rings.py
/runtime/
    /infra/
    /os/
    helix.py
/sandbox/
    /domain_data/
    /layers/
    /experiments/
```

## SECTION 4 — Move Operations
- `sandbox/helix.py` → `runtime/helix.py`
- `runtime/substrate_resolution.py` → `protocol/substrate_resolution.py`
- `sandbox/data` → `sandbox/domain_data`

## SECTION 5 — Dependency Violations
Status: **CLEAN.** Ring 0 contains zero upward imports. All runtime/sandbox components now reference `runtime.infra`.

## SECTION 6 — Deletion Simulation Results
System can execute `python runtime/helix.py --help` without `/sandbox/` present.
System can validate Ring 0 via `python protocol/validate_rings.py` without `/sandbox/` present.
**VERDICT: ARCHITECTURE_SECURE.**

## SECTION 7 — Obstruction Log
- **WITNESS_ABSENT:** No circular dependencies found.
- **ONTOLOGY_LEAK:** All core primitives consolidated.
- **INFRA_LEAK:** Infrastructure isolated to Ring 2.
