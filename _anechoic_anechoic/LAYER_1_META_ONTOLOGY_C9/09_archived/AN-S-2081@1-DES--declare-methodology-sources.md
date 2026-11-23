---
atom_family: SPEC
atom_id: AN-S-2081
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

Declare METHODOLOGY_SOURCES

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//METHODOLOGY_SOURCES.ID == "CA-SU-10";

Scope Unit//METHODOLOGY_SOURCES.Name == "METHODOLOGY_SOURCES";

Scope Unit//METHODOLOGY_SOURCES.Label == "SUPERLAYER";

Scope Unit//METHODOLOGY_SOURCES.order.ordered == true;

Scope Unit//METHODOLOGY_SOURCES.order.number == 1;

Scope Unit//METHODOLOGY_SOURCES ((IS_CONTAINED_BY)) Scope Unit//FRAMEWORK_METHODOLOGY
```

