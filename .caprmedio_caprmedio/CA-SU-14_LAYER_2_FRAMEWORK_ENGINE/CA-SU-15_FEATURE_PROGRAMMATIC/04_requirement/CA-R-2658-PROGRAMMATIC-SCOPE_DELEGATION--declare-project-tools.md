---
identity:
  atom_id: CA-R-2658
  ref_id: CA-R-2658
context:
  container:
    scope_unit: CA-SU-15
  role: Requirement
  form: Scope Delegation
  topics:
    main_subject: CAPRMEDIO_STRUCTURE <+ Scope Unit//PROJECT_TOOLS
  tier: 3
state:
  status: Active
  version: 5
  updated_at: '2026-11-12T15:04:13+00:00'
destination:
  file:
    name: CA-R-2658-PROGRAMMATIC-SCOPE_DELEGATION--declare-project-tools.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/04_requirement
---
## Summary

Declare PROJECT_TOOLS

## Claim

### Prose Claim

Plan / Work Report remains admitted only for an already admitted Task with the same Container and within the selected target boundary.

For every admitted local Atom, the Header.Container-derived IS_CONTAINED_BY target must be exactly `Scope Unit//PROJECT_TOOLS` (`CA-SU-19`). Its HAS_ACTIVE_SUBJECT target is closed to exactly the declared model entities or declared instances resolved at these Current local main Subject addresses:
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Data Handling/Serialization`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Delivery`
- `Subject/CAPRMEDIO/Graph/Node/Aspect/Engineering/Storage/Directory Layout`
- `Subject/CAPRMEDIO/Graph/Node/Project Model/History/Journal.Record`
- `Subject/CAPRMEDIO/Graph/Node/Project Model/Implementation`
- `Subject/CAPRMEDIO/Graph/Node/Project Model/Implementation/Code/Tool`

The selection contains exact objects only, not strings, type members, or descendants; an unresolved address grants no admission.
