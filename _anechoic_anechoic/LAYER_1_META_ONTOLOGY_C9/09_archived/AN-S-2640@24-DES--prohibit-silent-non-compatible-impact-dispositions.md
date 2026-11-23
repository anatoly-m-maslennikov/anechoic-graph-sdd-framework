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
  version: 24
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary
Prohibit silent non-compatible Impact dispositions

## Claim scope

the selection of non-compatible Impact dispositions.

## Claim

TOOLING **must not** select `update_required`, `replacement_required`, **or** `uncertain` **without** an explicit governed disposition.
