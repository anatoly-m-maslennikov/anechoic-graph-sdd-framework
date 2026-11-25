---
atom_family: SPEC
atom_id: AN-S-3609
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 29
  updated_at: 2026-11-04 16:52:59 +0400
---
## Summary

Define Plan blocking

## Claim

### Formal Claim

```CFEL
# model
Relation//BLOCKS <((HAS_INVERSE)) Relation//IS_BLOCKED_BY;

Relation//BLOCKS ((HAS_CLASSIFICATION)) Derivation == Derived;

# instances
Atom/(.Header.Context.Role: Plan)//$prerequisite ((BLOCKS)) Atom/(.Header.Context.Role: Plan)//$dependent
```

## Semantics

BLOCKS relates a prerequisite Plan to a dependent Plan that may start only after that prerequisite is Done.
