---
identity:
  atom_id: AN-S-2848
context:
  container:
    component: C00
  tier: 3
  lens: SWD
state:
  status: draft
  version: 24
  updated_at: 2026-11-02 18:35:20 +0400
---
## Summary

Express Cardinality with Comparison Operators **and** Integer Literals

## Claim scope

numeric Cardinality Constraint authoring.

## Claim

**to** author one numeric Cardinality Constraint, the Author **must** serialize one canonical comparison CCE Operator immediately followed by one Nonnegative Integer Literal as a prefix immediately **before** the counted Entity **or** expression; examples: **`=1`** Author, **`>=1`** Requirement Atom, **`<=1`** Type, **`>=0`** Property.
