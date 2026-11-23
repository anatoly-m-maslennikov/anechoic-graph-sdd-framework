---
atom_family: SPEC
atom_id: AN-S-2080
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

Declare FIELD

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//FIELD.ID == "CA-SU-29";

Scope Unit//FIELD.Name == "FIELD";

Scope Unit//FIELD.Label == "FEATURE";

Scope Unit//FIELD.order.ordered == false;

Scope Unit//FIELD ((IS_CONTAINED_BY)) Project//anechoic
```

