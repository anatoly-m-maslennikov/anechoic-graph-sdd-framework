---
identity:
  atom_id: CA-R-3183
  ref_id: CA-R-3183@1-draft
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
  updated_at: '2026-11-18T22:04:59.022525+00:00'
destination:
  file:
    name: CA-R-3183@1-draft-CORE_META_MODEL-REQUIREMENT--define-decision-and-standard-effects.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Define Decision and Standard effects

## Claim

### Prose Claim

A Decision directly affects a specific part of its owning Component's Realization. A Standard directly affects the whole Realization of its owning Component and all descendant Components. Both have the Realization effect; the Solution and Policy templates have the Specification effect.

## Details

Acceptance: a Decision owned by Component A applies to its specified part of A's Realization; a Standard owned by A covers A's Realization and that of child and deeper descendant Components. A sibling outside A's descendant tree is not included by that Standard's scope.

Sources: CA-A-1462@1-draft, CA-P-3082@1. Task: CA-P-3082.
