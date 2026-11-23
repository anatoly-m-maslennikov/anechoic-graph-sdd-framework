---
atom_family: SPEC
atom_id: AN-S-2093
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

Declare PROJECT_ACTIONS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//PROJECT_ACTIONS.ID == "CA-SU-39";

Scope Unit//PROJECT_ACTIONS.Name == "PROJECT_ACTIONS";

Scope Unit//PROJECT_ACTIONS.Label == "FEATURE_GROUP";

Scope Unit//PROJECT_ACTIONS.order.ordered == false;

Scope Unit//PROJECT_ACTIONS ((IS_CONTAINED_BY)) Scope Unit//SINGLE_ACTIONS
```

