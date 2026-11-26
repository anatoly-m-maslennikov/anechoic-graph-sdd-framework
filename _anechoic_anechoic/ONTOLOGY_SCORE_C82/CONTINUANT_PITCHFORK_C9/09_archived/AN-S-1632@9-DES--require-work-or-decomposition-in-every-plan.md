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
  version: 9
  updated_at: 2026-10-19 15:53:33 +0400
---
## Summary

Require work or decomposition in every Plan

# Summary

Require work or decomposition in every Plan

## Scope

Plan Atoms and their work or decomposition.

## Claim

**every** Plan Atom **must** have **`>=1`** of:

- its own work content;
- **`>0`** outgoing `DECOMPOSES_INTO` Relations **to** other Plan Atoms.

both contributions **may** be present within the same Claim; a Summary alone **without** either contribution is insufficient.

## Details
