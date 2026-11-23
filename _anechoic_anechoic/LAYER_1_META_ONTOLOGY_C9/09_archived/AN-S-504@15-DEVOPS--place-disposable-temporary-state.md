---
atom_family: SPEC
atom_id: AN-S-504
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 09:42:52 +0400
---
## Summary

Place Disposable Temporary State

# Summary

Place Disposable Temporary State

## Scope

disposable temporary state in a ANECHOIC Project.

## Claim

the ANECHOIC Project **must** place disposable scratch, staging, test cache, atomic-write intermediate, build intermediate, **and** interrupted-cleanup Carriers under `.anechoic_tmp/`.

## Details

deleting `.anechoic_tmp/` **must not** delete governed authority, Project Journal history, installed Framework Engine releases, runtime logs, sessions, databases, service state, **or** resumable state.
