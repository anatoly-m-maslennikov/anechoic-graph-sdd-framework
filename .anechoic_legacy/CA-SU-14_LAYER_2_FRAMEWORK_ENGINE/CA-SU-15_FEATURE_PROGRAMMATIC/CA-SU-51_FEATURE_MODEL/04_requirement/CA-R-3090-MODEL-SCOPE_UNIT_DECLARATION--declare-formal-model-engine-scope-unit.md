---
identity:
  atom_id: CA-R-3090
  ref_id: CA-R-3090
context:
  role: requirement
  form: scope_unit_declaration
  tier: 3
  container:
    scope_unit: CA-SU-51
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//FORMAL_MODEL_GENERATOR
state:
  version: 4
  status: active
  updated_at: '2026-11-13T17:44:23.397974+00:00'
destination:
  file:
    name: CA-R-3090-MODEL-SCOPE_UNIT_DECLARATION--declare-formal-model-engine-scope-unit.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-51_FEATURE_MODEL/04_requirement
---
## Summary

Declare FORMAL MODEL ENGINE Scope Unit

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name="FORMAL_MODEL_GENERATOR",
    instance=ScopeUnit(
        id="CA-SU-50",
        name="FORMAL_MODEL_GENERATOR",
        structural_level=4,
        label="FEATURE",
        ordered=False,
        container="MODEL",
    ),
)
```
