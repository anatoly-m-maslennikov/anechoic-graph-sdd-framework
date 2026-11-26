---
atom_family: SPEC
atom_id: AN-S-469
container:
  component: C9
tier: 6
context:
  lens: DevOps
state:
  status: archived
  version: 26
  updated_at: 2026-10-29 10:13:50 +0400
---
## Summary

Serialize Atomic Admission Strictness

## Claim scope

an explicit atomic admission strictness selection in the Framework Instance Settings TOML Carrier.

## Claim

an explicit atomic admission strictness selection **in** the Framework Instance Settings TOML Carrier **must** use `creation_strictness` **in** `[artifacts]`, using the allowed values governed by CA-R-1630.
