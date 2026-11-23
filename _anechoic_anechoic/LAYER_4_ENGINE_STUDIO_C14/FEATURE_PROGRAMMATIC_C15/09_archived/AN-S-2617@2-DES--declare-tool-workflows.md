---
atom_family: SPEC
atom_id: AN-S-2617
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-08 23:18:49 +0400
---
## Summary

Declare TOOL_WORKFLOWS

## Claim

### Formal Claim

```CFEL
# instances
Scope Unit//TOOL_WORKFLOWS.ID == "CA-SU-18";

Scope Unit//TOOL_WORKFLOWS.Name == "TOOL_WORKFLOWS";

Scope Unit//TOOL_WORKFLOWS.Label == "FEATURE";

Scope Unit//TOOL_WORKFLOWS.order.ordered == false;

Scope Unit//TOOL_WORKFLOWS ((IS_CONTAINED_BY)) Scope Unit//PROGRAMMATIC
```


### Prose Claim

The explicit default Role/Form pairs below are: `Requirement/Requirement`, `Requirement/Declaration`, `Requirement/Scope Delegation`, `Method/Decision`, `Evaluation/Decision`, `Evaluation/Eval Case`, `Delivery/Decision`, `Operations/Decision`, `Operations/Workflow`, `Operations/Step`, `Operations/Action`. Existing global default admissions, including existing Declaration families, remain unchanged; no additional pairs are granted. No exact Current Solution, Direct Policy, or Approach Policy Role/Form pair is selected. Implementation / Code Synopsis remains admitted by the global default, and Plan / Work Report remains admitted only for an already admitted Task with the same Container and within the selected target boundary.

For every admitted local Atom, the Header.Container-derived IS_CONTAINED_BY target must be exactly `Scope Unit//TOOL_WORKFLOWS` (`CA-SU-18`). Its HAS_ACTIVE_SUBJECT target is closed to exactly the declared model entities or declared instances resolved at these Current local main Subject addresses:
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Architecture/Communication`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Serialization`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Source Selection`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Execution Control/Effect Authorization`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Storage`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Storage/Directory Layout`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Verification/Dynamic Testing`
- `Subject/ANECHOIC/Graph/Node/Project Model/Atom`
- `Subject/ANECHOIC/Graph/Node/Project Model/Governing Configuration`
- `Subject/ANECHOIC/Graph/Node/Project Model/Scope Unit`
- `Subject/ANECHOIC/Graph/Rule`

The selection contains exact objects only, not strings, type members, or descendants; an unresolved address grants no admission.