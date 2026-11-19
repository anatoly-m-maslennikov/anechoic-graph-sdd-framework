---
identity:
  atom_id: CA-R-3190
  ref_id: CA-R-3190@1-draft
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
  updated_at: '2026-11-18T22:05:18.738009+00:00'
destination:
  file:
    name: CA-R-3190@1-draft-CORE_META_MODEL-REQUIREMENT--check-exports-at-the-named-unit-boundary.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Check exports at the named Unit boundary

## Claim

### Prose Claim

A Unit-level export allows callers to import the named Unit directly. A caller importing the containing Module requires a Module-level export. Check each named import against its own export, provider visibility, applicable caller rules, and the layer direction in CA-R-3169.

## Details

Acceptance: when only `billing.api.run` is exported and the caller is otherwise allowed, accept `from billing.api import run` and reject an import of `billing.api` as a Module.

Sources: CA-A-1463@1-draft. Task: CA-P-3084.
