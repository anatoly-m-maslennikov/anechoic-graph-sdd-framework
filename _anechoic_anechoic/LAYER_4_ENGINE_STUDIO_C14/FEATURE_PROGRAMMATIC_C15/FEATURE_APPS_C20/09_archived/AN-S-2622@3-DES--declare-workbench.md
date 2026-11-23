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
  version: 3
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Declare WORKBENCH

## Claim


### Prose Claim

The receiving Scope Unit is WORKBENCH. Existing default Role and Form admissions remain applicable. The additional local Role/Form pairs are exactly:

- Delivery / Solution;
- Method / Direct Policy;
- Requirement / Direct Policy;
- Requirement / Solution;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `ANECHOIC_MODEL <+ Project`;
- `ANECHOIC_MODEL <+ Projection`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Authoring <+ Query Authoring <+ SQL`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Execution Control`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Storage`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Temporary State`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Performance <+ Measurement and Profiling`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Test Design`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//CODEX_EXTENSION`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//WORKBENCH_BACKEND`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//WORKBENCH_FRONTEND`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Component Structure`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to WORKBENCH. The Scope Unit identity, Parent, responsibility and structural tree are unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//WORKBENCH.ID == "CA-SU-43";

Scope Unit//WORKBENCH.Name == "WORKBENCH";

Scope Unit//WORKBENCH.Label == "APP";

Scope Unit//WORKBENCH.order.ordered == false;

Scope Unit//WORKBENCH ((IS_CONTAINED_BY)) Scope Unit//APPS
```
