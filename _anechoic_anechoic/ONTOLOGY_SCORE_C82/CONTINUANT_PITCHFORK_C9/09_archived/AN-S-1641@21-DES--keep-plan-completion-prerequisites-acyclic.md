---
atom_family: SPEC
atom_id: AN-S-1641
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-29 07:45:27 +0400
---
## Summary

Keep Plan completion prerequisites acyclic

## Claim scope

Plan execution.

## Claim

Plan execution **must not** contain a cycle of completion prerequisites, including one formed jointly by `BLOCKS` **and** the requirement **to** complete directly contained Plan work **before** its containing Plan can be Done **or** Canceled.

## Details
