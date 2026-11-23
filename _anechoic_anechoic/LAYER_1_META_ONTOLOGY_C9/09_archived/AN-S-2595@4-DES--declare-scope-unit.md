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
  version: 4
  updated_at: 2026-11-05 12:58:42 +0400
---


## Summary

Declare Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Continuant

class ScopeUnit(Continuant):
    pass

declare_entity(entity_class=ScopeUnit, entity_name="Scope Unit", classifications={"Container": "yes"})
```

```CFEL
# instances
Scope Unit//$scope_unit {::0+}((CONTAINS)) Atom//$atom;

Scope Unit//$scope_unit{::0..1}((IS_CONTAINED_BY)) Scope Unit//$scope_unit_2;

Scope Unit//$scope_unit_3{::0+}((CONTAINS)) Scope Unit//$scope_unit_4;

Scope Unit//$unit;

IF (($unit not in (Scope Unit/Project//$scope_unit_5)) AND ($unit.ID != "CA-SU--1"))
THEN ($unit {==1}((IS_CONTAINED_BY)) Scope Unit//$scope_unit_6);
```

## Semantics

A Scope Unit defines a boundary of responsibility for Atoms.
