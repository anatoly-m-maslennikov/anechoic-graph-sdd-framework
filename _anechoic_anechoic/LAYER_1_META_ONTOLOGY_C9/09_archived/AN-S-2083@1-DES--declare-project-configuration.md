---
atom_family: SPEC
atom_id: AN-S-2083
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:07:49 +0400
---
## Summary

Declare PROJECT_CONFIGURATION

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//PROJECT_CONFIGURATION.ID == "CA-SU-13";

Scope Unit//PROJECT_CONFIGURATION.Name == "PROJECT_CONFIGURATION";

Scope Unit//PROJECT_CONFIGURATION.Label == "LAYER";

Scope Unit//PROJECT_CONFIGURATION.order.ordered == true;

Scope Unit//PROJECT_CONFIGURATION.order.number == 3;

Scope Unit//PROJECT_CONFIGURATION ((IS_CONTAINED_BY)) Scope Unit//METHODOLOGY_SOURCES
```

