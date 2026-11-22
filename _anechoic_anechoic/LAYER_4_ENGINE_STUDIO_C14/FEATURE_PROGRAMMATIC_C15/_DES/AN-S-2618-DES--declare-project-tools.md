---
atom_family: SPEC
atom_id: AN-S-2618
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-12T15:04:13+00:00'
---
## Summary

Declare PROJECT_TOOLS

## Claim

### Prose Claim

Plan / Work Report remains admitted only for an already admitted Task with the same Container and within the selected target boundary.

For every admitted local Atom, the Header.Container-derived IS_CONTAINED_BY target must be exactly `Scope Unit//PROJECT_TOOLS` (`CA-SU-19`). Its HAS_ACTIVE_SUBJECT target is closed to exactly the declared model entities or declared instances resolved at these Current local main Subject addresses:
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Serialization`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery`
- `Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Storage/Directory Layout`
- `Subject/ANECHOIC/Graph/Node/Project Model/History/Journal.Record`
- `Subject/ANECHOIC/Graph/Node/Project Model/Implementation`
- `Subject/ANECHOIC/Graph/Node/Project Model/Implementation/Code/Tool`

The selection contains exact objects only, not strings, type members, or descendants; an unresolved address grants no admission.
