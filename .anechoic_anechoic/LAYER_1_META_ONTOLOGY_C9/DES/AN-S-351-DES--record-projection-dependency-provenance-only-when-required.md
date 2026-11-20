---
identity:
  atom_id: AN-S-351
context:
  container:
    component: C9
  tier: 2
  lens: DES
state:
  status: active
  version: 21
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary
Record Projection dependency provenance **only** **when** required

## Claim

### Prose Claim

Projections.

a Projection **must** record dependency provenance **only** **when** its registered job requires that information; no Projection is required **to** persist a blanket source frontier.

this conditional recording obligation does **not** remove source traceability required by `CA-R-2535-CORE_META_MODEL-CORE-REQUIREMENT--define-projection-artifact-form` **or** a more specific admitted Projection specification.
