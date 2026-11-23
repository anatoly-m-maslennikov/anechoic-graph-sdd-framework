---
atom_family: SPEC
atom_id: AN-S-2085
container:
  component: C16
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:07:49 +0400
---
## Summary

Declare SINGLE_ACTIONS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//SINGLE_ACTIONS.ID == "CA-SU-31";

Scope Unit//SINGLE_ACTIONS.Name == "SINGLE_ACTIONS";

Scope Unit//SINGLE_ACTIONS.Label == "FEATURE_GROUP";

Scope Unit//SINGLE_ACTIONS.order.ordered == false;

Scope Unit//SINGLE_ACTIONS ((IS_CONTAINED_BY)) Scope Unit//TOOLS
```

