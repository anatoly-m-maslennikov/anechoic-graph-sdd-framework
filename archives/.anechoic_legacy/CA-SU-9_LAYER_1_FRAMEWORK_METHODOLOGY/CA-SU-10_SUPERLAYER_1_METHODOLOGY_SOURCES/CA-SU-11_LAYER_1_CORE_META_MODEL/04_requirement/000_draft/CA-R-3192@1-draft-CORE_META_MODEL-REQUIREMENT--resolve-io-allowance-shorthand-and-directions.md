---
identity:
  atom_id: CA-R-3192
  ref_id: CA-R-3192@1-draft
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
  updated_at: '2026-11-18T22:05:24.338602+00:00'
destination:
  file:
    name: CA-R-3192@1-draft-CORE_META_MODEL-REQUIREMENT--resolve-io-allowance-shorthand-and-directions.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Resolve io_allowance shorthand and directions

## Claim

### Prose Claim

Resolve one `io_allowance` as an allowlist or a directional object. `io_allowance: [db, api]` applies to both directions. `input` covers reads and receives; `output` covers writes and sends. An omitted direction inherits that direction from the nearest ancestor. `[]` or `false` denies all direct I/O, while an omitted allowance with no ancestor defaults to `all`.

## Details

Acceptance: `[db, api]` permits both input and output for those channels; `{input: [db], output: []}` permits db input and denies output; a child that overrides only `input` keeps the nearest inherited `output`; no ancestor plus an omitted allowance resolves to `all`. Reject treating an omitted direction as `all` when an ancestor supplies it, or treating `false` as inheritance.

Sources: CA-A-1463@1-draft. Task: CA-P-3085.
