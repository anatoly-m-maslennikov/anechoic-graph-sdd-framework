---
atom_family: SPEC
atom_id: AN-S-2096
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

Declare WORKFLOW_SCHEDULER

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//WORKFLOW_SCHEDULER.ID == "CA-SU-42";

Scope Unit//WORKFLOW_SCHEDULER.Name == "WORKFLOW_SCHEDULER";

Scope Unit//WORKFLOW_SCHEDULER.Label == "FEATURE_GROUP";

Scope Unit//WORKFLOW_SCHEDULER.order.ordered == false;

Scope Unit//WORKFLOW_SCHEDULER ((IS_CONTAINED_BY)) Scope Unit//SCHEDULERS
```

