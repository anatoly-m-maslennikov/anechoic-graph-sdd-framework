---
atom_family: SPEC
atom_id: AN-S-2848
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 21
  updated_at: 2026-10-29 10:13:50 +0400
---
## Summary

Express Cardinality with Comparison Operators **and** Integer Literals

## Claim scope

numeric Cardinality Constraint authoring.

## Claim

**to** author one numeric Cardinality Constraint, the Author **must** serialize one canonical comparison CCE Operator immediately followed by one Nonnegative Integer Literal as a prefix immediately **before** the counted Entity **or** expression; examples: **`=1`** Author, **`>=1`** Requirement Atom, **`<=1`** Type, **`>=0`** Property.
