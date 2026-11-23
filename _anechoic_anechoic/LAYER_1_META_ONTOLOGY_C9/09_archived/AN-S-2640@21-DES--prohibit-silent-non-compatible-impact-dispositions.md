---
atom_family: SPEC
atom_id: AN-S-2640
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-29 07:17:15 +0400
---
## Summary

Prohibit silent non-compatible Impact dispositions

# Prohibit silent non-compatible Impact dispositions

## Scope

the selection of non-compatible Impact dispositions.

## Claim

TOOLING **must not** select `update_required`, `replacement_required`, **or** `uncertain` **without** an explicit governed disposition.

## Details
