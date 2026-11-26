---
atom_family: SPEC
atom_id: AN-S-1592
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 28
  updated_at: "2026-11-25T22:24:05.177055+00:00"
---
## Summary
Separate Governed Transitions from Status Values

## Claim

### Prose Claim

Artifact Revision Status values associated with admission, acceptance, commitment, activation, completion, **or** archival.

an Artifact Revision Status value **must** remain distinct from the Action **or** Workflow whose execution **may** establish that value.

## Details
the same distinction applies **when** a Workflow uses several Steps **to** establish the Status value.
