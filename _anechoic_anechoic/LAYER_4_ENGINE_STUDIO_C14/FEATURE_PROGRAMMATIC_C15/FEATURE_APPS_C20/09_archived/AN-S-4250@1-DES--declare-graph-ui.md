---
atom_family: SPEC
atom_id: AN-S-4250
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-02 19:07:49 +0400
---
## Summary

Declare GRAPH_UI

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//GRAPH_UI.ID == "CA-SU-44";

Scope Unit//GRAPH_UI.Name == "GRAPH_UI";

Scope Unit//GRAPH_UI.Label == "APP";

Scope Unit//GRAPH_UI.order.ordered == false;

Scope Unit//GRAPH_UI ((IS_CONTAINED_BY)) Scope Unit//APPS
```

