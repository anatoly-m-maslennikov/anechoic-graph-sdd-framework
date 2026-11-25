---
atom_family: SPEC
atom_id: AN-S-2732
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Declare CONTRIBUTES_TO

## Claim

### Formal Claim

```CFEL
# model
Relation//CONTRIBUTES_TO ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
Atom//$contributor ((CONTRIBUTES_TO)) Atom//$contribution
```

## Semantics

The Host contributes toward the Target. Contribution is distinct from verified satisfaction of a Requirement.
