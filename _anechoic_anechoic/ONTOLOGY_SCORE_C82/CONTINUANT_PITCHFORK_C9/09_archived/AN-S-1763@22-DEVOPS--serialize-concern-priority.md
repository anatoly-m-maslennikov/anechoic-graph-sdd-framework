---
atom_family: SPEC
atom_id: AN-S-1763
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 22
  updated_at: 2026-10-29 10:13:50 +0400
---
## Summary

Serialize Concern Priority

## Claim scope

Concern Atom Carriers and non-Concern Content Role Atom Carriers.

## Claim

a Concern Atom Carrier **must** serialize **`=1`** selected Priority as `priority` with the lowercase value `high`, `medium`, **or** `low`. **every** non-Concern Content Role Atom Carrier **must** omit `priority`; virtual `highest` **must not** be stored.
