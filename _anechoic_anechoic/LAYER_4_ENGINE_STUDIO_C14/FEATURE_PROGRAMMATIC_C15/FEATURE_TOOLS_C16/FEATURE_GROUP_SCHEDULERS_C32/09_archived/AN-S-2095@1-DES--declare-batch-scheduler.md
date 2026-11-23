---
atom_family: SPEC
atom_id: AN-S-2095
container:
  component: C32
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:07:49 +0400
---
## Summary

Declare BATCH_SCHEDULER

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//BATCH_SCHEDULER.ID == "CA-SU-41";

Scope Unit//BATCH_SCHEDULER.Name == "BATCH_SCHEDULER";

Scope Unit//BATCH_SCHEDULER.Label == "FEATURE_GROUP";

Scope Unit//BATCH_SCHEDULER.order.ordered == false;

Scope Unit//BATCH_SCHEDULER ((IS_CONTAINED_BY)) Scope Unit//SCHEDULERS
```

