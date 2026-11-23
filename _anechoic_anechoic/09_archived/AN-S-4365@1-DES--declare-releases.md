---
atom_family: SPEC
atom_id: AN-S-4365
container:
  component: C00
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:07:49 +0400
---
## Summary

Declare RELEASES

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//RELEASES.ID == "CA-SU-27";

Scope Unit//RELEASES.Name == "RELEASES";

Scope Unit//RELEASES.Label == "LAYER";

Scope Unit//RELEASES.order.ordered == true;

Scope Unit//RELEASES.order.number == 5;

Scope Unit//RELEASES ((IS_CONTAINED_BY)) Project//anechoic
```

