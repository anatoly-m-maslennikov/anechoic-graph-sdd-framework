---
atom_family: SPEC
atom_id: AN-S-1079
container:
  component: C16
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reject non-current upstream version

# Reject non-current upstream version

## Claim checked

the commit flow cannot seal **or** apply a typed upstream relation whose target version is **not** current immediately **before** the file change.

## Test case

prepare one `UPDATE` fixture whose direct upstream target is at version 3, **then** supply a candidate context that names version 2 for that same target.

## Acceptance criteria

the flow returns a deterministic non-current-upstream-version diagnostic, names both versions, **and** creates no governed **or** Git state change.

## Failure disposition

reject the flow **if** it accepts, silently rewrites, **or** omits the stale target reference.
