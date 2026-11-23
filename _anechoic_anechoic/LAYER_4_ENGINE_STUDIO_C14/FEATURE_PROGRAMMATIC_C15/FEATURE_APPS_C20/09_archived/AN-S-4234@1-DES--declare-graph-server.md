---
atom_family: SPEC
atom_id: AN-S-4234
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

Declare GRAPH_SERVER

## Claim

### Formal Claim

```CFEL
Scope Unit//GRAPH_SERVER.ID == "CA-SU-43";
Scope Unit//GRAPH_SERVER.Name == "GRAPH_SERVER";
Scope Unit//GRAPH_SERVER.Label == "APP";
Scope Unit//GRAPH_SERVER.order.ordered == false;
Scope Unit//GRAPH_SERVER ((IS_CONTAINED_BY)) Scope Unit//APPS
```

