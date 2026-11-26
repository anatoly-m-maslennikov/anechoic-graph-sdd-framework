---
atom_family: SPEC
atom_id: AN-S-1632
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 24
  updated_at: 2026-10-29 10:13:49 +0400
---
## Summary

Require work or decomposition in every Plan

## Claim scope

Plan Atoms, their own work, and their direct Plan containment.

## Claim

**every** Plan Atom **must** have **`>=1`** of:

- its own work content;
- **`>0`** outgoing derived `CONTAINS` links **to** directly contained Plan Atoms.

both contributions **may** be present within the same Claim; a Summary alone **without** either contribution is insufficient.
