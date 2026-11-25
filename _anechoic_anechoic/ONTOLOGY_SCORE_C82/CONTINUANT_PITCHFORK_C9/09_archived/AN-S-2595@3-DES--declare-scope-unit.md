---
atom_family: SPEC
atom_id: AN-S-2595
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-04 11:00:07 +0400
---

## Summary

Declare Scope Unit

## Claim

### Formal Claim

```CFEL
# model
Scope Unit >| (Container == yes);

Scope Unit ((NARROWER_THAN)) Continuant;

# instances
Scope Unit//$scope_unit {::0+}((CONTAINS)) Atom//$atom;

Scope Unit//$scope_unit{::0..1}((IS_CONTAINED_BY)) Scope Unit//$scope_unit_2;

Scope Unit//$scope_unit_3{::0+}((CONTAINS)) Scope Unit//$scope_unit_4;

IF (Scope Unit//$unit not in (Scope Unit/Project//$scope_unit_5))
THEN ($unit {==1}((IS_CONTAINED_BY)) Scope Unit//$scope_unit_6);
```

## Semantics

A Scope Unit defines a boundary of responsibility for Atoms.
