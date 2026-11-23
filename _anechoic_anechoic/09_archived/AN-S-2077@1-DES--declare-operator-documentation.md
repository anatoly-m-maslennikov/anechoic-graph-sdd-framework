---
atom_family: SPEC
atom_id: AN-S-2077
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

Declare OPERATOR_DOCUMENTATION

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//OPERATOR_DOCUMENTATION.ID == "CA-SU-25";

Scope Unit//OPERATOR_DOCUMENTATION.Name == "OPERATOR_DOCUMENTATION";

Scope Unit//OPERATOR_DOCUMENTATION.Label == "LAYER";

Scope Unit//OPERATOR_DOCUMENTATION.order.ordered == true;

Scope Unit//OPERATOR_DOCUMENTATION.order.number == 3;

Scope Unit//OPERATOR_DOCUMENTATION ((IS_CONTAINED_BY)) Project//anechoic
```

