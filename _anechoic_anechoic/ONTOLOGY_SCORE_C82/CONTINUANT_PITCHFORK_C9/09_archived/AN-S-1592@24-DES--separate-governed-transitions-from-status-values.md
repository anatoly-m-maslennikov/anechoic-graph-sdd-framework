---
atom_family: SPEC
atom_id: AN-S-1592
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 24
  updated_at: 2026-10-27 19:59:53 +0400
---
## Summary

Separate Governed Transitions from Status Values

# Summary
Separate Governed Transitions from Status Values

## Scope
Artifact Revision Status values associated with admission, acceptance, commitment, activation, completion, **or** archival.

## Claim
an Artifact Revision Status value **must** remain distinct from the Action **or** Workflow whose execution **may** establish that value.

## Details
the same distinction applies **when** a Workflow uses several Steps **to** establish the Status value.
