---
identity:
  atom_id: CA-R-2654
  ref_id: CA-R-2654@3
context:
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//PROGRAMMATIC
  tier: 3
  container:
    scope_unit: CA-SU-14
state:
  status: Archived
  version: 3
  updated_at: 2026-11-09 07:45:15 +0400
destination:
  file:
    name: CA-R-2654@3-FRAMEWORK_ENGINE-SCOPE_DELEGATION--declare-programmatic.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/04_requirement/archive
---

## Summary

Declare PROGRAMMATIC

## Claim

### Prose Claim

The receiving Scope Unit is PROGRAMMATIC. Existing default Role and Form admissions remain applicable. The additional local Role/Form pairs are exactly:

- Delivery / Direct Policy;
- Evaluation / Approach Policy;
- Evaluation / Direct Policy;
- Evaluation / Solution;
- Method / Direct Policy;
- Method / Solution;
- Requirement / Direct Policy;
- Requirement / Solution;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Indexing`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Query Processing`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Schema`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ State Synchronization`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//APPS`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//CONNECTOR_TOOLS`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//MCP`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//PROJECT_TOOLS`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//TOOLS`;
- `ANECHOIC_STRUCTURE <+ Scope Unit//TOOL_WORKFLOWS`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery/Change Readiness`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery/Reproducibility`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Communication`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Communication/Interface Contracts`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Component Structure`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Authoring/Code Authoring`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Authoring/Code Authoring/Python Code`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Configuration`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Data Validation`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Source Retrieval`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Code Hot Reload`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Effect Authorization`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Failure Handling`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Outcome Reporting`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Resource Limits`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Observability/Logging`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Storage/Directory Layout`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Storage/Temporary State`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Performance/Measurement and Profiling`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Traceability`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Traceability/Provenance`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Coverage`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Dynamic Testing`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Dynamic Testing/Canary Testing`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Static Analysis`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Static Analysis/Python Code`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification/Test Design`;
- `Subject/ANECHOIC/Graph/Node/Aspect/UX/Discovery and Navigation`;
- `Subject/ANECHOIC/Graph/Node/Aspect/UX/Result and Status Presentation`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Project.Settings.Temporary State`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to PROGRAMMATIC. The Scope Unit identity, Parent, responsibility and structural tree are unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//PROGRAMMATIC.ID == "CA-SU-15";

Scope Unit//PROGRAMMATIC.Name == "PROGRAMMATIC";

Scope Unit//PROGRAMMATIC.Label == "FEATURE";

Scope Unit//PROGRAMMATIC.order.ordered == false;

Scope Unit//PROGRAMMATIC ((IS_CONTAINED_BY)) Scope Unit//FRAMEWORK_ENGINE
```
