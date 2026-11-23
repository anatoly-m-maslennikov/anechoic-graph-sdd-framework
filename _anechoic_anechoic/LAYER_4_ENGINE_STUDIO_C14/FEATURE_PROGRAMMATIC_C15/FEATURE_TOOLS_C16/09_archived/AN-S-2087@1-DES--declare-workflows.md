---
atom_family: SPEC
atom_id: AN-S-2087
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

Declare WORKFLOWS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//WORKFLOWS.ID == "CA-SU-33";

Scope Unit//WORKFLOWS.Name == "WORKFLOWS";

Scope Unit//WORKFLOWS.Label == "FEATURE_GROUP";

Scope Unit//WORKFLOWS.order.ordered == false;

Scope Unit//WORKFLOWS ((IS_CONTAINED_BY)) Scope Unit//TOOLS
```

