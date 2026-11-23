---
atom_family: SPEC
atom_id: AN-S-2674
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-11-11 15:37:01 +0400
---
## Summary

Derive Recursive Containment from Direct Containment

## Claim

### Formal Claim

```CFEL
# model
$container ((RECURSIVELY_CONTAINS)) $descendant;

Relation//RECURSIVELY_CONTAINS ((HAS_CLASSIFICATION)) Derivation == Derived
```

## Semantics

The Host recursively contains the Target when one or more successive `CONTAINS` links lead from Host to Target. Intermediate Entities need only satisfy the endpoint constraints of `CONTAINS`. Derive this Relation from the existing links.
