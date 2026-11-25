---
atom_family: SPEC
atom_id: AN-S-3032
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:01:22.424808+00:00'
---
## Summary

Resolve Anechoic Project tree paths

## Claim

### Prose Claim

Resolve all tree roots from the selected Project directory. REAL covers the
Project outside its records directory. SPEC covers `.anechoic_<project_name>/`
outside `_PMETA/` and `__TKT/`. Those subdirectories are the PMETA and TKT
roots.

## Details

- Anechoic uses `.anechoic_anechoic/` as its records directory.
- Each selected Project in a monorepo uses paths relative to its own root.
- A Component Spec Section shares `draft/` and `archived/` across lenses.
  Active SPEC carriers live in their lens directories.
- Active TKT carriers live directly under `__TKT/TASKS/` or `__TKT/ISSUES/`.
  Each branch has its own `draft/`, `archived/`, `done/`, `canceled/`, and
  `resolved/` status directories. Backlog uses the branch’s `backlog/`.
- Linked Ticket assets use the Ticket’s directory. Standalone Ticket
  assets use `__TKT/ASSETS/` with the same status directory convention.
- PMETA Active carriers live at the `_PMETA/` root, with shared `draft/`
  and `archived/` folders.

Acceptance: a source file classifies as REAL. An ordinary records file
classifies as SPEC. Files under the two reserved subdirectories each
classify only under their respective logical tree.

Source: CA-A-1461@1-draft. Task: CA-P-3079.
