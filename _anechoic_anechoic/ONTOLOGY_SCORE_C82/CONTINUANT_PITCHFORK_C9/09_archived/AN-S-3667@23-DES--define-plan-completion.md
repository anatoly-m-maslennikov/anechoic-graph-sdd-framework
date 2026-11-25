---
atom_family: SPEC
atom_id: AN-S-3667
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 23
  updated_at: 2026-10-29 07:17:17 +0400
---
## Summary

Define Plan completion

# Summary

Define Plan completion

## Scope

Plan completion.

## Claim

Plan Status Done **means** that **all** applicable completion conditions hold:

- the Plan satisfies CA-R-1575; absence of own work **and** directly contained Plans **must not** count as completion.
- its own work, **if** present, is complete.
- **every** directly contained Plan has terminal Status Done **or** Canceled; mixed terminal statuses are allowed.
- its Definition of Done falsifying Condition Expression evaluates **to** false.

a containing Plan Atom whose Status is Done **or** Canceled requires every directly contained Plan to have terminal Status Done **or** Canceled; mixed terminal statuses are allowed, and a child Status need not match the parent. A child with Status Canceled satisfies this terminal-child condition without claiming its own work is complete; a child with Status Archived does **not** satisfy it. For parent Status Done, the parent's own work **if** present must be complete and its Definition of Done falsifying expression must be false; those Done conditions do **not** apply merely because parent Status is Canceled.

## Details
