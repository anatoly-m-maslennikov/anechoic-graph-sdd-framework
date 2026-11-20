---
identity:
  atom_id: CA-R-3191
  ref_id: CA-R-3191@1-draft
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
  updated_at: '2026-11-18T22:05:21.679730+00:00'
destination:
  file:
    name: CA-R-3191@1-draft-CORE_META_MODEL-REQUIREMENT--define-one-inherited-io-allowance-per-component-manifest.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define one inherited io_allowance per Component Manifest

## Claim

### Prose Claim

A Component Manifest has one `io_allowance` field. It applies to the Component's own modules and ordinary Packages; it is not split into separate own and children allowances. A child Component uses the nearest ancestor's allowance by default and may declare one explicit override in its own Manifest. An ordinary Package may further narrow the allowance it inherits.

## Details

Acceptance: a child with no declaration resolves the nearest ancestor's value; a child with an explicit declaration resolves that value while the parent's authored value stays unchanged. Reject a model that uses a farther ancestor when a nearer declaration exists, or introduces separate own/children allowance fields.

Sources: CA-A-1463@1-draft. Task: CA-P-3085.
