---
atom_family: SPEC
atom_id: AN-S-4249
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

Declare WORKFLOW_ORCHESTRATOR

## Claim


### Prose Claim

The receiving Scope Unit is WORKFLOW_ORCHESTRATOR. Existing default Role and Form admissions remain applicable. No additional local Role/Form pair is needed.

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `Subject/ANECHOIC/Carrier`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Communication`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Data Validation`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Recovery`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Dynamic Testing`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Execution/Workflow Run.Coverage`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to WORKFLOW_ORCHESTRATOR. The Scope Unit identity, Parent, responsibility and structural tree are unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//WORKFLOW_ORCHESTRATOR.ID == "CA-SU-2";

Scope Unit//WORKFLOW_ORCHESTRATOR.Name == "WORKFLOW_ORCHESTRATOR";

Scope Unit//WORKFLOW_ORCHESTRATOR.Label == "APP";

Scope Unit//WORKFLOW_ORCHESTRATOR.order.ordered == false;

Scope Unit//WORKFLOW_ORCHESTRATOR ((IS_CONTAINED_BY)) Scope Unit//APPS
```
