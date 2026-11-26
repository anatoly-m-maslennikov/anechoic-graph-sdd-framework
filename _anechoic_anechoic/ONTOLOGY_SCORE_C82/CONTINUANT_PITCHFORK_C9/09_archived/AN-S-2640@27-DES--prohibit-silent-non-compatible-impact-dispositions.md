---
atom_family: SPEC
atom_id: AN-S-2640
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: "archived"
  version: 27
  updated_at: "2026-11-25T23:11:43.986536+00:00"
---
## Summary
Prohibit silent non-compatible Impact dispositions

## Claim

### Prose Claim


the selection of non-compatible Impact dispositions.


TOOLING **must not** select `update_required`, `replacement_required`, **or** `uncertain` **without** an explicit governed disposition.
