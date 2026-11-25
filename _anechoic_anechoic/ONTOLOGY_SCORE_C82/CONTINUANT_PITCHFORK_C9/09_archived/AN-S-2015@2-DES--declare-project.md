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
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---

## Summary

Declare Project

## Claim

A Project uses ANECHOIC's MODEL.

```CFEL
Scope Unit/Project;
Scope Unit/Project//{:1};
Project >| (Container == yes);
Project// {:0}((IS_CONTAINED_BY)) Scope Unit//;
Project ((NARROWER_THAN)) @Scope Unit
```

## Semantics

A Project is the root Scope Unit.
