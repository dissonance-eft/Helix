# Meta-Kernel Discovery Lab Protocol

## Purpose
The Meta-Kernel Lab automatically proposes candidate structural axes from domain objects and attempts to mathematically destroy them. Only structurally invariant, non-tautological axes survive.

## Execution
Run a full suite:
`python engine/meta_kernel_lab.py`

Run a bounded CI suite (faster, 5k perms):
`python engine/meta_kernel_lab.py --bounded`

## Outputs
- `artifacts/meta_kernel/*`: Holds all raw and compressed candidate matrices, scores, and registry.
- `docs/meta_kernel_report.md`: Summary of discovery run.
- `docs/meta_kernel_falsifiers.md`: Auto-generated break conditions for any surviving axes.
