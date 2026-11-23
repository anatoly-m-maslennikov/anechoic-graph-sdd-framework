---
atom_family: SPEC
atom_id: AN-S-4410
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-10 08:07:21 +0400
---

## Summary

Declare GRAPH_UI

## Claim


### Prose Claim

The receiving Scope Unit is GRAPH_UI. Existing default Role and Form admissions remain applicable. The additional local Role/Form pairs are exactly:

- Method / Solution;
- Delivery / Solution;
- Requirement / Rule;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Delivery <+ Packaging`;

- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Storage`;

- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Output Publication`;

- `Subject/ANECHOIC/Graph/Node/Aspect/UX/Interaction/Accessibility`;

- `Subject/ANECHOIC/Graph/Node/Aspect/UX/Discovery and Navigation`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to GRAPH_UI. The Scope Unit identity, Parent, responsibility and structural tree are unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//GRAPH_UI.ID == "CA-SU-44";

Scope Unit//GRAPH_UI.Name == "GRAPH_UI";

Scope Unit//GRAPH_UI.Label == "APP";

Scope Unit//GRAPH_UI.order.ordered == false;

Scope Unit//GRAPH_UI ((IS_CONTAINED_BY)) Scope Unit//APPS
```
