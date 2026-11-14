---
identity:
  atom_id: CA-R-3147
  ref_id: CA-R-3147
context:
  role: requirement
  form: scope_delegation
  tier: 3
  container:
    scope_unit: CA-SU-51
  topics:
    main_subject: CAPRMEDIO_STRUCTURE <+ Scope Unit//MODEL_VALIDATION
state:
  version: 1
  status: active
  updated_at: '2026-11-13T17:44:29.441875+00:00'
destination:
  file:
    name: CA-R-3147-MODEL-SCOPE_DELEGATION--delegate-model-validation-responsibilities.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-51_FEATURE_MODEL/04_requirement
---
## Summary

Delegate MODEL VALIDATION responsibilities

## Claim

### Prose Claim

The receiving Scope Unit is MODEL_VALIDATION. Its admitted Main Subject is the declared instance `CAPRMEDIO_STRUCTURE <+ Scope Unit//MODEL_VALIDATION`.

Provide the shared API that Tools and Apps call to validate proposed instances before writing. Apply the generated Model's applicable Property and Relation rules, including inherited rules. Run named instance checks supplied from their Declarations through a separate checks module. CA-R-3137 governs write validation.
