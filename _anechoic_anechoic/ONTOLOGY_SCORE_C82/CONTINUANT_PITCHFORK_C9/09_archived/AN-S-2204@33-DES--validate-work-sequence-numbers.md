---
atom_family: SPEC
atom_id: AN-S-2204
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 33
  updated_at: 2026-10-29 10:13:50 +0400
---
## Summary

Validate Work Sequence Numbers

## Claim scope

supplied Work Sequence Numbers for Plans directly contained by the same Plan or sharing the same top-level Plan container.

## Claim

**every** supplied Work Sequence Number **must** be a unique positive ordinal among Plans directly contained by the same Plan **or** sharing the same top-level Plan container.
