---
identity:
  atom_id: CA-R-3134
  ref_id: CA-R-3134
context:
  role: requirement
  form: scope_delegation
  tier: 3
  container:
    scope_unit: CA-SU-15
  topics:
    main_subject: CAPRMEDIO_STRUCTURE <+ Scope Unit//MODEL
state:
  version: 2
  status: active
  updated_at: '2026-11-13T17:43:08.763166+00:00'
destination:
  file:
    name: CA-R-3134-PROGRAMMATIC-SCOPE_DELEGATION--delegate-model-responsibilities.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/04_requirement
---
## Summary

Delegate MODEL responsibilities

## Claim

### Prose Claim

The receiving Scope Unit is MODEL. Its admitted Main Subjects are these declared Scope Unit instances:

- `CAPRMEDIO_STRUCTURE <+ Scope Unit//MODEL`.
- `CAPRMEDIO_STRUCTURE <+ Scope Unit//FORMAL_MODEL_GENERATOR`.
- `CAPRMEDIO_STRUCTURE <+ Scope Unit//GENERATED_MODEL`.
- `CAPRMEDIO_STRUCTURE <+ Scope Unit//MODEL_VALIDATION`.

FORMAL_MODEL_GENERATOR validates the complete selected set of Python Model Declarations and builds GENERATED_MODEL. GENERATED_MODEL holds the generated Python classes and objects. MODEL_VALIDATION provides the shared API that Tools and Apps use to validate proposed instances before writing.

Named instance checks are authored in their Declarations and made available to MODEL_VALIDATION through a separate checks module outside GENERATED_MODEL.
