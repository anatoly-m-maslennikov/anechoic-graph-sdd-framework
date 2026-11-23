---
atom_family: SPEC
atom_id: AN-S-2266
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

Declare FRAMEWORK_ENGINE

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//FRAMEWORK_ENGINE.ID == "CA-SU-14";

Scope Unit//FRAMEWORK_ENGINE.Name == "FRAMEWORK_ENGINE";

Scope Unit//FRAMEWORK_ENGINE.Label == "LAYER";

Scope Unit//FRAMEWORK_ENGINE.order.ordered == true;

Scope Unit//FRAMEWORK_ENGINE.order.number == 2;

Scope Unit//FRAMEWORK_ENGINE ((IS_CONTAINED_BY)) Project//anechoic
```

