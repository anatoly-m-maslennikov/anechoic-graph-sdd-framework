---
atom_family: SPEC
atom_id: AN-S-2620
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-09 07:45:15 +0400
---

## Summary

Declare MCP

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//MCP.ID == "CA-SU-21";

Scope Unit//MCP.Name == "MCP";

Scope Unit//MCP.Label == "FEATURE";

Scope Unit//MCP.order.ordered == false;

Scope Unit//MCP ((IS_CONTAINED_BY)) Scope Unit//PROGRAMMATIC
```


### Prose Claim

The receiving Scope Unit is MCP. Existing default Role and Form admissions remain applicable. No additional local Role/Form pair is needed.

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Development/Architecture/Communication`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Data Validation`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Output Publication`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Data Handling/Source Selection`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Effect Authorization`;
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Storage`;
- `Subject/ANECHOIC/Graph/Node/Aspect/UX/Discovery and Navigation`;
- `Subject/ANECHOIC/Graph/Node/Aspect/UX/Entry`;
- `Subject/ANECHOIC/Graph/Node/Aspect/UX/Result and Status Presentation`;
- `Subject/ANECHOIC/Graph/Node/Project Model/Project`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to MCP. The Scope Unit identity, Parent, responsibility and structural tree are unchanged.
