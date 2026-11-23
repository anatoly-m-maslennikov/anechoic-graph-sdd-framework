---
atom_family: SPEC
atom_id: AN-S-351
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 9
  updated_at: 2026-10-19 15:53:15 +0400
---
## Summary

Record Projection dependency provenance **only** **when** required

# Summary
Record Projection dependency provenance **only** **when** required

## Scope
Projections.

## Claim
a Projection **must** record dependency provenance **only** **when** its registered job requires that information; no Projection is required **to** persist a blanket source frontier.

this conditional recording obligation does **not** remove source traceability required by `CA-R-1746-CORE_META_MODEL-CORE-REQUIREMENT--define-projection-artifact-form` **or** a more specific admitted Projection specification.

## Details
