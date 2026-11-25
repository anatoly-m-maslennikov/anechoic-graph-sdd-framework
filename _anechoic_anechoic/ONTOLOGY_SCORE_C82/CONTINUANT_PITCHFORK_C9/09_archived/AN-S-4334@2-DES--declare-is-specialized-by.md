---
atom_family: SPEC
atom_id: AN-S-4334
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 19:46:41 +0400
---

## Summary

Declare IS_SPECIALIZED_BY

## Claim

### Formal Claim

```CFEL
# model
Relation//IS_SPECIALIZED_BY <((HAS_INVERSE)) Relation//SPECIALIZES;

Relation//IS_SPECIALIZED_BY ((HAS_CLASSIFICATION)) Derivation == Derived;

# instances
Atom//$parent ((IS_SPECIALIZED_BY)) Atom//$child
```

## Semantics

IS_SPECIALIZED_BY relates an Atom to an Atom whose Claim specializes its Claim.
