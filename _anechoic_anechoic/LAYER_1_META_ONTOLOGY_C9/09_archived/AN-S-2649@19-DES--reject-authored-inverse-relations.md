---
atom_family: SPEC
atom_id: AN-S-2649
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 19
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Reject authored inverse relations

# Summary

Reject authored inverse relations

## Scope

authored inverse typed relations.

## Claim

validators **must** reject **every** inverse typed relation authored **in** an Atom Carrier.

## Details

Inverse means the derived direction declared by the governing Relation Kind definition, not a direction guessed from its name. In the containment pair, IS_CONTAINED_BY is direct from child to parent and is the only permitted authoritative direction when Atom containment is authored; CONTAINS is the inverse and must not be separately authored. This clarification does not admit a new runtime relation key or waive endpoint Graph Rules.
