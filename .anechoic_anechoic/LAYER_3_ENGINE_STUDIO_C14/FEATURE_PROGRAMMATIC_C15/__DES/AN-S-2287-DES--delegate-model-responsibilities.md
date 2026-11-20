---
atom_family: SPEC
atom_id: AN-S-2287
structure:
  container:
    component: C15
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T17:43:08.763166+00:00'
---
## Summary

Delegate MODEL responsibilities

## Claim

### Prose Claim

The receiving Scope Unit is MODEL. Its admitted Main Subjects are these declared Scope Unit instances:

- `ANECHOIC_STRUCTURE <+ Scope Unit//MODEL`.
- `ANECHOIC_STRUCTURE <+ Scope Unit//FORMAL_MODEL_GENERATOR`.
- `ANECHOIC_STRUCTURE <+ Scope Unit//GENERATED_MODEL`.
- `ANECHOIC_STRUCTURE <+ Scope Unit//MODEL_VALIDATION`.

FORMAL_MODEL_GENERATOR validates the complete selected set of Python Model Declarations and builds GENERATED_MODEL. GENERATED_MODEL holds the generated Python classes and objects. MODEL_VALIDATION provides the shared API that Tools and Apps use to validate proposed instances before writing.

Named instance checks are authored in their Declarations and made available to MODEL_VALIDATION through a separate checks module outside GENERATED_MODEL.
