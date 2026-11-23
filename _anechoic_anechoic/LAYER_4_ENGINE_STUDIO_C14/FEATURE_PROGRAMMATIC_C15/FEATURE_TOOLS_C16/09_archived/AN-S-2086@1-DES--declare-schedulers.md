---
atom_family: SPEC
atom_id: AN-S-2086
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

Declare SCHEDULERS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//SCHEDULERS.ID == "CA-SU-32";

Scope Unit//SCHEDULERS.Name == "SCHEDULERS";

Scope Unit//SCHEDULERS.Label == "FEATURE_GROUP";

Scope Unit//SCHEDULERS.order.ordered == false;

Scope Unit//SCHEDULERS ((IS_CONTAINED_BY)) Scope Unit//TOOLS
```

