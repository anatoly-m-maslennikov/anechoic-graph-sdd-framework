---
atom_family: SPEC
atom_id: AN-S-2567
container:
  component: C9
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 10
  updated_at: 2026-10-29 07:45:30 +0400
---
## Summary
Reconcile Development Backlog candidates **after** release

## Claim scope
Development Backlog candidates **after** a Release Record is accepted.

## Claim

ANECHOIC **must** reconcile the Development Backlog against its exact released manifest as follows:

- remove a candidate whose promoted Atoms were fully delivered **in** that release.
- **every** candidate that is unfinished, partially delivered, excluded, **or** newly deferred **must** remain unscheduled **or** move **to** another target version.
- a candidate **must not** be removed as shipped **unless** the released manifest accounts for its promoted Atoms.

## Details
