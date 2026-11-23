---
atom_family: SPEC
atom_id: AN-S-2264
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:07:49 +0400
---
## Summary

Declare CORE_META_MODEL

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//CORE_META_MODEL.ID == "CA-SU-11";

Scope Unit//CORE_META_MODEL.Name == "CORE_META_MODEL";

Scope Unit//CORE_META_MODEL.Label == "LAYER";

Scope Unit//CORE_META_MODEL.order.ordered == true;

Scope Unit//CORE_META_MODEL.order.number == 1;

Scope Unit//CORE_META_MODEL ((IS_CONTAINED_BY)) Scope Unit//METHODOLOGY_SOURCES
```

