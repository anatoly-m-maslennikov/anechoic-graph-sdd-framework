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
  version: 5
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Declare MCP

## Claim


### Prose Claim

The receiving Scope Unit is MCP. The additional local Role/Form pairs are exactly:

- Method / Solution;
- Delivery / Solution;

- Requirement / Rule;

- Concern / Question;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Data Validation`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Output Publication`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Effect Authorization`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Discovery and Navigation`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Entry`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ UX <+ Result and Status Presentation`;
- `MODEL//ANECHOIC <+ Project`;

- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Execution Control <+ Resource Limits`;

### Formal Claim

```CFEL
# instances
Scope Unit//MCP.ID == "CA-SU-21";

Scope Unit//MCP.Name == "MCP";

Scope Unit//MCP.Label == "FEATURE";

Scope Unit//MCP.order.ordered == false;

Scope Unit//MCP ((IS_CONTAINED_BY)) Scope Unit//PROGRAMMATIC
```
