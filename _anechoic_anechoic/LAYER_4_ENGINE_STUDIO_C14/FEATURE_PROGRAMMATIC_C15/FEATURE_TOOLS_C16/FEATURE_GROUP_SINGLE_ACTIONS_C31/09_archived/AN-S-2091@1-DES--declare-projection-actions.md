---
atom_family: SPEC
atom_id: AN-S-2091
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

Declare PROJECTION_ACTIONS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//PROJECTION_ACTIONS.ID == "CA-SU-37";

Scope Unit//PROJECTION_ACTIONS.Name == "PROJECTION_ACTIONS";

Scope Unit//PROJECTION_ACTIONS.Label == "FEATURE_GROUP";

Scope Unit//PROJECTION_ACTIONS.order.ordered == false;

Scope Unit//PROJECTION_ACTIONS ((IS_CONTAINED_BY)) Scope Unit//SINGLE_ACTIONS
```

