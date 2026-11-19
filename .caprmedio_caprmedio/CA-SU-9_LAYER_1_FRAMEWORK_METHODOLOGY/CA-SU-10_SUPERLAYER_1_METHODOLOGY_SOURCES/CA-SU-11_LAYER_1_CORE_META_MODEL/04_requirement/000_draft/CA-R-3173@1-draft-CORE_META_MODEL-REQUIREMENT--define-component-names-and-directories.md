---
identity:
  atom_id: CA-R-3173
  ref_id: CA-R-3173@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:03:05.305699+00:00'
destination:
  file:
    name: CA-R-3173@1-draft-CORE_META_MODEL-REQUIREMENT--define-component-names-and-directories.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define Component names and directories

## Claim

### Prose Claim

Migrate each Scope Unit ID to a Component ID using its existing number, for example `CA-SU-43` becomes `C43`. Compose the logical Component Name from its Label and name, allowing conditional prefixes and postfixes. Policy filters can match this logical name, for example `component.name: ADAPTER_*`. Use the logical Name and stable Component ID in the directory layout `(LAYER_<layer number>)_<Name>_C<ID>`; the Layer prefix is optional.

## Details

Acceptance: migrating CA-SU-43 preserves 43 as C43; a Component directory includes its logical Name and stable ID with or without the optional layer prefix.

Sources: CA-A-1461@1-draft, CA-A-1463@1-draft. Task: CA-P-3079.
