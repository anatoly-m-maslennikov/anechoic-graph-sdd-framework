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
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Declare WORKBENCH_FRONTEND

## Claim

### Prose Claim

Own the Workbench query UI, component palette, presentation, formatting, page navigation and frontend state. Shared Workbench requirements and cross-interface contracts remain in WORKBENCH.

The receiving Scope Unit is WORKBENCH_FRONTEND. The additional local Role/Form pairs are exactly:

- Method / Solution;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `MODEL//ANECHOIC <+ Projection`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery <+ Packaging`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Code Authoring`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspect//Visual Design`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Libraries and Frameworks`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Component Authoring`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Frontend Engineering <+ Code Style`;

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH_FRONTEND.ID == "CA-SU-46";

Scope Unit//WORKBENCH_FRONTEND.Name == "WORKBENCH_FRONTEND";

Scope Unit//WORKBENCH_FRONTEND.Label == "FEATURE";

Scope Unit//WORKBENCH_FRONTEND.order.ordered == false;

Scope Unit//WORKBENCH_FRONTEND ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```
