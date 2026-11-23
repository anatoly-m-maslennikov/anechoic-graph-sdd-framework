---
atom_family: SPEC
atom_id: AN-S-1606
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-29 10:13:48 +0400
---
## Summary

Keep Summary fixed for Atom identity

## Claim scope

the Summary of an Atom across its Revisions.

## Claim

an Atom **must** keep the Summary created with it across **all** of its Revisions. **if** its Summary needs a change, **then** it **must** be replaced by a new Atom with a new Atom ID, even **if** its Claim is unchanged.
