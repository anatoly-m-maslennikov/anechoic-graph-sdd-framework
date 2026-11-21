---
atom_family: SPEC
atom_id: AN-S-2567
container:
  component: C27
tier: 4
context:
  lens: DES
state:
  status: active
  version: 16
  updated_at: 2026-11-09 15:54:30 +0400
---

## Summary
Reconcile Development Backlog candidates **after** release

## Claim

### Prose Claim

Development Backlog candidates **after** a Release Record is accepted.


ANECHOIC **must** reconcile the Development Backlog against its exact released manifest as follows:

- remove a candidate whose promoted Atoms were fully delivered **in** that release.
- **every** candidate that is unfinished, partially delivered, excluded, **or** newly deferred **must** remain unscheduled **or** move **to** another target version.
- a candidate **must not** be removed as shipped **unless** the released manifest accounts for its promoted Atoms.
