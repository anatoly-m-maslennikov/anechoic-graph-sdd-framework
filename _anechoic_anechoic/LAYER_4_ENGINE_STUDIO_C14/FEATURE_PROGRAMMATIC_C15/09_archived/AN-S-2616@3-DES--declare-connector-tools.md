---
atom_family: SPEC
atom_id: AN-S-2616
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Declare CONNECTOR_TOOLS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//CONNECTOR_TOOLS.ID == "CA-SU-17";

Scope Unit//CONNECTOR_TOOLS.Name == "CONNECTOR_TOOLS";

Scope Unit//CONNECTOR_TOOLS.Label == "FEATURE";

Scope Unit//CONNECTOR_TOOLS.order.ordered == false;

Scope Unit//CONNECTOR_TOOLS ((IS_CONTAINED_BY)) Scope Unit//PROGRAMMATIC
```


### Prose Claim

The explicit default Role/Form pairs below are: `Requirement/Requirement`, `Requirement/Declaration`, `Requirement/Scope Delegation`, `Method/Decision`, `Evaluation/Decision`, `Evaluation/Eval Case`, `Delivery/Decision`, `Operations/Decision`, `Operations/Workflow`, `Operations/Step`, `Operations/Action`. Existing global default admissions, including existing Declaration families, remain unchanged; no additional pairs are granted. No exact Current Solution, Direct Policy, or Approach Policy Role/Form pair is selected. Analysis & Advisory / Code Synopsis remains admitted by the global default, and Plan / Work Report remains admitted only for an already admitted Task with the same Container and within the selected target boundary.

For every admitted local Atom, the Header.Container-derived IS_CONTAINED_BY target must be exactly `Scope Unit//CONNECTOR_TOOLS` (`CA-SU-17`). Its HAS_ACTIVE_SUBJECT target is closed to exactly the declared model entities or declared instances resolved at these Current local main Subject addresses:
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Serialization`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Retrieval`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Data Handling <+ Source Selection`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Delivery`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Operation <+ Storage <+ Directory Layout`
- `PROJECT STRUCTURE//ANECHOIC <+ Aspects <+ Engineering <+ Quality <+ Verification <+ Dynamic Testing`
- `MODEL//ANECHOIC <+ Governing Configuration`
- `MODEL//ANECHOIC <+ Scope Unit`

The selection contains exact objects only, not strings, type members, or descendants; an unresolved address grants no admission.