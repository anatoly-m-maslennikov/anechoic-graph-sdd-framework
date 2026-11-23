---
identity:
  atom_id: CA-R-3168
  ref_id: CA-R-3168@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:01:22.424808+00:00'
destination:
  file:
    name: CA-R-3168@1-draft-CORE_META_MODEL-REQUIREMENT--resolve-anechoic-project-tree-paths.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
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
