---
atom_family: SPEC
atom_id: AN-S-1641
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: "archived"
  version: 23
  updated_at: "2026-11-26T09:59:57.617090+00:00"
---
## Summary

Keep Plan completion prerequisites acyclic

## Claim

### Prose Claim


Plan execution.


Plan execution **must not** contain a cycle of completion prerequisites, including one formed jointly by `BLOCKS` **and** the requirement **to** complete directly contained Plan work **before** its containing Plan can be Done **or** Canceled.
