---
atom_family: SPEC
atom_id: AN-S-1729
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: active
  version: 29
  updated_at: '2026-11-25T21:19:17.265702+00:00'
---
## Summary

Warn About Selected-sibling Claim Boundaries

## Claim

### Prose Claim


A Claim scoped to selected sibling Components or legacy Scope Units.


**when** **`=1`** Atom Claim concerns **only** **`>=2`** selected siblings **and** does **not** apply **to** their parent as a whole, the Evaluation **must** report a non-blocking boundary warning for review; that restriction alone **must not** make the Atom invalid **or** trigger automatic rejection, splitting, **or** retargeting **to** their parent.
