---
atom_family: SPEC
atom_id: AN-S-75
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Reject an invalid staged governed commit

# Reject an invalid staged governed commit

## Claim checked

the Git gate accepts a real-change boundary **only** **when** its staged target set exactly matches one sealed action **and** its Initiative message projection.

## Test case

Present the gate with an unresolved target, stale expected revision, a Journal carrier mixed with a real-change target, two atomic targets, an incomplete bulk target set, **and** one valid sealed target set.

## Acceptance criteria

Each invalid state returns one stable diagnostic **before** commit creation. The valid state creates **only** the sealed real-change target commit **and** does **not** require a Journal record **or** Journal carrier **in** the index.

## Failure disposition

Reject the delivery **if** an invalid boundary passes, a valid boundary fails, **or** preflight mutates repository state.
