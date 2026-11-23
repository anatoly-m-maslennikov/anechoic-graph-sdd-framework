---
atom_family: SPEC
atom_id: AN-S-2624
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-09 17:00:18 +0400
---

## Summary

Declare WORKBENCH_FRONTEND

## Claim

### Prose Claim

Own the Workbench query UI, component palette, presentation, formatting, page navigation and frontend state. Shared Workbench requirements and cross-interface contracts remain in WORKBENCH.

The receiving Scope Unit is WORKBENCH_FRONTEND. Existing default Role and Form admissions remain applicable. The additional local Role/Form pairs are exactly:

- Method / Solution;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `ANECHOIC_MODEL <+ Projection`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Delivery <+ Packaging`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL`;
- `PROJECT_STRUCTURE <+ Aspect//Visual Design`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to WORKBENCH_FRONTEND. The Scope Unit identity, Parent, responsibility and structural tree are unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH_FRONTEND.ID == "CA-SU-46";

Scope Unit//WORKBENCH_FRONTEND.Name == "WORKBENCH_FRONTEND";

Scope Unit//WORKBENCH_FRONTEND.Label == "FEATURE";

Scope Unit//WORKBENCH_FRONTEND.order.ordered == false;

Scope Unit//WORKBENCH_FRONTEND ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```
