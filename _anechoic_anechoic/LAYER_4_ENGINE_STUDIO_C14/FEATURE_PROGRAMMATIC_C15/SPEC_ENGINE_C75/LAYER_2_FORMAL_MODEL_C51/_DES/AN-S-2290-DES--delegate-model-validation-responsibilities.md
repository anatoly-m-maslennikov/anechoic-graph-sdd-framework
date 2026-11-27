---
atom_family: SPEC
atom_id: AN-S-2290
concern:
  subject: "Model"
  path: "ANECHOIC"
  relation: "is_contained_by"
container:
  component: C51
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Delegate MODEL VALIDATION responsibilities

## Claim

### Prose Claim

The receiving Scope Unit is MODEL_VALIDATION. Its admitted Main Subject is the declared instance `ANECHOIC_STRUCTURE <+ Scope Unit//MODEL_VALIDATION`.

Provide the shared API that Tools and Apps call to validate proposed instances before writing. Apply the generated Model's applicable Property and Relation rules, including inherited rules. Run named instance checks supplied from their Declarations through a separate checks module. CA-R-3137 governs write validation.
