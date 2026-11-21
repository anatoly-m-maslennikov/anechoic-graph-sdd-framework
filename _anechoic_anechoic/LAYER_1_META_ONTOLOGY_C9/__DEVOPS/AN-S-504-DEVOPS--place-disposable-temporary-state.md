---
atom_family: SPEC
atom_id: AN-S-504
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 22
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Place Disposable Temporary State

## Claim

### Prose Claim


disposable temporary state in a ANECHOIC Project.


the ANECHOIC Project **must** place disposable scratch, staging, test cache, atomic-write intermediate, build intermediate, **and** interrupted-cleanup Carriers under `.anechoic_tmp/`.

## Details

deleting `.anechoic_tmp/` **must not** delete governed authority, Project Journal history, installed Framework Engine releases, runtime logs, sessions, databases, service state, **or** resumable state.
