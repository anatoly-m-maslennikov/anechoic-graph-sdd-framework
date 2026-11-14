---
identity:
  atom_id: CA-R-2657
  ref_id: CA-R-2657
context:
  container:
    scope_unit: CA-SU-15
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: CAPRMEDIO_STRUCTURE <+ Scope Unit//TOOL_WORKFLOWS
  tier: 3
state:
  status: Active
  version: 3
  updated_at: '2026-11-12T15:04:13+00:00'
destination:
  file:
    name: CA-R-2657-PROGRAMMATIC-SCOPE_DELEGATION--declare-tool-workflows.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/04_requirement
---
## Summary

Declare TOOL_WORKFLOWS

## Claim

### Prose Claim

Plan / Work Report remains admitted only for an already admitted Task with the same Container and within the selected target boundary.

For every admitted local Atom, the Header.Container-derived IS_CONTAINED_BY target must be exactly `Scope Unit//TOOL_WORKFLOWS` (`CA-SU-18`). Its HAS_ACTIVE_SUBJECT target is closed to exactly the declared model entities or declared instances resolved at these Current local main Subject addresses:
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Architecture/Communication`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Data Handling/Serialization`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Data Handling/Source Selection`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Execution Control`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Execution Control/Effect Authorization`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Storage`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Storage/Directory Layout`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Verification/Dynamic Testing`
- `Subject/CAPRMEDIO/Graph/Node/Project Model/Atom`
- `Subject/CAPRMEDIO/Graph/Node/Project Model/Governing Configuration`
- `Subject/CAPRMEDIO/Graph/Node/Project Model/Scope Unit`
- `Subject/CAPRMEDIO/Graph/Rule`

The selection contains exact objects only, not strings, type members, or descendants; an unresolved address grants no admission.
