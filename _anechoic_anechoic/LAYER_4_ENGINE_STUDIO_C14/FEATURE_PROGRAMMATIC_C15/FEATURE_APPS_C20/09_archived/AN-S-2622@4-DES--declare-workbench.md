---
atom_family: SPEC
atom_id: AN-S-2622
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Declare WORKBENCH

## Claim


### Prose Claim

The receiving Scope Unit is WORKBENCH. The additional local Role/Form pairs are exactly:

- Delivery / Solution;
- Method / Direct Policy;
- Requirement / Direct Policy;
- Requirement / Rule;
- Requirement / Solution;

- Concern / Problem;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Observability <+ Logging`;

- `MODEL//ANECHOIC <+ Project`;
- `MODEL//ANECHOIC <+ Workspace`;
- `MODEL//ANECHOIC <+ View`;
- `MODEL//ANECHOIC <+ Projection`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Design`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//CODEX_EXTENSION`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//WORKBENCH_BACKEND`;
- `PROJECT STRUCTURE//ANECHOIC <+ Scope Unit//WORKBENCH_FRONTEND`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Component Structure`;


### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH.ID == "CA-SU-43";

Scope Unit//WORKBENCH.Name == "WORKBENCH";

Scope Unit//WORKBENCH.Label == "APP";

Scope Unit//WORKBENCH.order.ordered == false;

Scope Unit//WORKBENCH ((IS_CONTAINED_BY)) Scope Unit//APPS
```
