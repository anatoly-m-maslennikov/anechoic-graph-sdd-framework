---
identity:
  atom_id: CA-R-3193
  ref_id: CA-R-3193@1-draft
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
  updated_at: '2026-11-18T22:05:27.109259+00:00'
destination:
  file:
    name: CA-R-3193@1-draft-CORE_META_MODEL-REQUIREMENT--validate-effective-child-allowances-against-applicable-policy.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Validate effective child allowances against applicable Policy

## Claim

### Prose Claim

A parent Spec Policy can select child Component Manifests. For each selected child, validate its effective `io_allowance`—after nearest-ancestor inheritance and any explicit child override—against every applicable Policy. A violation reports the direction, channel, Policy, explicit reason, authored allowance, and effective allowance, then preserves the authored value; validation does not silently narrow or rewrite it.

## Details

Acceptance: a child whose effective input and output channels satisfy all applicable Policies passes; an over-broad direction fails with the named channel and Policy and leaves the authored child allowance unchanged. Reject a check that validates only the inherited default, omits the explicit child override, or mutates the value while reporting the violation.

Sources: CA-A-1463@1-draft. Task: CA-P-3085.
