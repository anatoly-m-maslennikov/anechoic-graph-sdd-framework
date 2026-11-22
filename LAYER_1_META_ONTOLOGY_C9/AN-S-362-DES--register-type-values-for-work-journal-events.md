---
atom_family: SPEC
atom_id: AN-S-362
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: active
  version: 41
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Register Type Values for Work Journal Events

## Claim

### Prose Claim


legacy Work Journal execution-observation category labels in serialized Journal Carrier Main Content.


the Main Content of a serialized Journal Carrier **must** preserve a supplied legacy Work Journal execution-observation category label as one of (Started, Progressed, Completed, Failed, Interrupted, Abandoned, Recovered).

this is a Carrier representation constraint. It does **not** create a logical Event Record Property, prescribe an Event Record business Action, or make these legacy observation labels model-level action values.
