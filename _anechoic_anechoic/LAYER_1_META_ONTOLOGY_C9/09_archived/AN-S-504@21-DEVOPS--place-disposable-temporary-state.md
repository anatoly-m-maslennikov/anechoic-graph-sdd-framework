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
  version: 21
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Place Disposable Temporary State

## Claim scope

disposable temporary state in a ANECHOIC Project.

## Claim

the ANECHOIC Project **must** place disposable scratch, staging, test cache, atomic-write intermediate, build intermediate, **and** interrupted-cleanup Carriers under `.anechoic_tmp/`.

## Details

deleting `.anechoic_tmp/` **must not** delete governed authority, Project Journal history, installed Framework Engine releases, runtime logs, sessions, databases, service state, **or** resumable state.
