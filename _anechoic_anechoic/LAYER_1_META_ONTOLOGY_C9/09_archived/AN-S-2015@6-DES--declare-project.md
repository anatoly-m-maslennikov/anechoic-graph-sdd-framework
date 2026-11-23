---
atom_family: SPEC
atom_id: AN-S-2015
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Declare Project

## Claim

### Prose Claim

A Project uses ANECHOIC's MODEL.

### Formal Claim

```CFEL
# model
Scope Unit/Project;

Project >| (Container == yes);

Project ((NARROWER_THAN)) Scope Unit;

# instances
Scope Unit/Project//$scope_unit{::1};

Project//$project {::0}((IS_CONTAINED_BY)) Scope Unit//$scope_unit_2;

Project//$project_2.order.ordered == false;

Project//$project_3.order.number:: []{::0}
```

## Semantics

A Project is the root Scope Unit. It is not renamed or moved through Scope Unit operations. Its one stable Scope Unit ID is governed by CA-R-2526. The shared model makes Project unordered with no order.number; individual Project Declarations inherit these facts.
