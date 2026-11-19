---
atom_id: CA-R-2668
ref_id: CA-R-2668
role: Requirement
form: Scope Unit Declaration
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//FIELD
tier: 3
status: active
version: 2
updated_at: '2026-11-12T18:32:26.904255+00:00'
container:
  scope_unit: CA-SU-00
destination:
  file:
    name: CA-R-2668-SCOPE_UNIT_DECLARATION--declare-field.md
    path: .anechoic_anechoic/04_requirement
---
## Summary

Declare FIELD

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ScopeUnit

declare_entity(
    entity_name='FIELD',
    instance=ScopeUnit(
        structural_level=1,
        id='CA-SU-29',
        name='FIELD',
        label='FEATURE',
        ordered=False,
        container='anechoic',
    ),
)
```

