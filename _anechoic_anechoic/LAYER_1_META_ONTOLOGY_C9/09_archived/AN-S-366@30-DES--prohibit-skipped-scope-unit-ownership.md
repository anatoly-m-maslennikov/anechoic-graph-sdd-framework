---
atom_family: SPEC
atom_id: AN-S-366
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 30
  updated_at: 2026-10-29 10:13:49 +0400
---
## Summary

Prohibit skipped Scope Unit ownership

## Claim scope

Scope Unit ownership through a stored structural-parent relation.

## Claim

a Scope Unit **must not** own a descendant Scope Unit through a stored structural-parent relation **when** another active Scope Unit lies between them.
