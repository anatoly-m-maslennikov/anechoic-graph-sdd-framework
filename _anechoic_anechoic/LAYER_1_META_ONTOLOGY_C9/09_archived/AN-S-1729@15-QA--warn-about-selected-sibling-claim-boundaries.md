---
atom_family: SPEC
atom_id: AN-S-1729
container:
  component: C9
tier: 2
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Warn About Selected-sibling Claim Boundaries

# Summary

Warn About Selected-sibling Claim Boundaries

## Scope

an Atom Claim concerning **only** selected sibling Scope Units.

## Claim

**when** **`=1`** Atom Claim concerns **only** **`>=2`** selected sibling Scope Units **and** does **not** apply **to** their containing Scope Unit as a whole, the Evaluation **must** report a non-blocking boundary warning for review; that restriction alone **must not** make the Atom invalid **or** trigger automatic rejection, splitting, **or** retargeting **to** their parent.

## Details
