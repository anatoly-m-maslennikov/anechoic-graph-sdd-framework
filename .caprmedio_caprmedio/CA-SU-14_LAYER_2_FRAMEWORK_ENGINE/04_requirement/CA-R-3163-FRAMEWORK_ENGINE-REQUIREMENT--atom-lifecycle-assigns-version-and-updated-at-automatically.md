---
identity:
  atom_id: CA-R-3163
  ref_id: CA-R-3163
context:
  role: requirement
  form: requirement
  container:
    scope_unit: CA-SU-14
  tier: 3
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Atom.Header.State.Version
state:
  version: 1
  status: active
  updated_at: '2026-11-13T20:27:53.588756+00:00'
destination:
  file:
    name: CA-R-3163-FRAMEWORK_ENGINE-REQUIREMENT--atom-lifecycle-assigns-version-and-updated-at-automatically.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/04_requirement
---
## Summary

Atom lifecycle assigns Version and Updated At automatically

## Claim

### Prose Claim

When a lifecycle operation creates a new Atom Version, the runtime assigns both Version and Updated At. Use Version 1 for a new Atom ID. For an existing ID, use one more than the highest Version across its Current, Draft and Archived carriers. Set Updated At to the creation time.

Promotion keeps the Draft’s Version and Updated At. The Draft Version may skip numbers and must be greater than the published predecessor’s Version.
