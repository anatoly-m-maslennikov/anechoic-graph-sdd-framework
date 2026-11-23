---
atom_family: SPEC
atom_id: AN-S-2078
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:07:49 +0400
---
## Summary

Declare CORE_EXTENSIONS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//CORE_EXTENSIONS.ID == "CA-SU-26";

Scope Unit//CORE_EXTENSIONS.Name == "CORE_EXTENSIONS";

Scope Unit//CORE_EXTENSIONS.Label == "LAYER";

Scope Unit//CORE_EXTENSIONS.order.ordered == true;

Scope Unit//CORE_EXTENSIONS.order.number == 4;

Scope Unit//CORE_EXTENSIONS ((IS_CONTAINED_BY)) Project//anechoic
```

