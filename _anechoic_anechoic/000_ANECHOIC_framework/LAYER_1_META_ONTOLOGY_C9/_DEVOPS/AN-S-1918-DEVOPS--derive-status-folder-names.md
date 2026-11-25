---
atom_family: SPEC
atom_id: AN-S-1918
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-11T19:37:43+04:00'
---

## Summary

Derive Status folder names

## Claim

### Prose Claim

For a Status with a folder, read the Status Order Number from its Requirement Declaration.

1. Write the number as three decimal digits with leading zeros.
2. Encode the Status name in lowercase snake case.
3. Join the number and name with one underscore.

Use this name for the `<status folder>` segment in the applicable Status Group's File Layout Claim.
