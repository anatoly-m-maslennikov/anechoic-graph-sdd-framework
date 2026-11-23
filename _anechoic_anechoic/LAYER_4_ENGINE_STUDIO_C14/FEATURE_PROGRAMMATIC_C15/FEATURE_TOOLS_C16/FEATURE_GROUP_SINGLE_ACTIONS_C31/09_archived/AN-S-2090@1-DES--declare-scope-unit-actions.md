---
atom_family: SPEC
atom_id: AN-S-2090
container:
  component: C31
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:07:49 +0400
---
## Summary

Declare SCOPE_UNIT_ACTIONS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//SCOPE_UNIT_ACTIONS.ID == "CA-SU-36";

Scope Unit//SCOPE_UNIT_ACTIONS.Name == "SCOPE_UNIT_ACTIONS";

Scope Unit//SCOPE_UNIT_ACTIONS.Label == "FEATURE_GROUP";

Scope Unit//SCOPE_UNIT_ACTIONS.order.ordered == false;

Scope Unit//SCOPE_UNIT_ACTIONS ((IS_CONTAINED_BY)) Scope Unit//SINGLE_ACTIONS
```

