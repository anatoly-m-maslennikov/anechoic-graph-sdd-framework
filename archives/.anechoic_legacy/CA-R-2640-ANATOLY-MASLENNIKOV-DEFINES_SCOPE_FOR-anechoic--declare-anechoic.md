---
atom_id: CA-R-2640
ref_id: CA-R-2640
container:
  scope_unit: CA-SU--1
role: Requirement
form: Scope Unit Declaration
topics:
  main_subject: ANECHOIC_STRUCTURE <+ Project//anechoic
tier: 3
status: active
version: 2
updated_at: 2026-11-05 12:58:42 +0400
carrier_destination:
  file:
    name: CA-R-2640-ANATOLY-MASLENNIKOV-DEFINES_SCOPE_FOR-anechoic--declare-anechoic.md
    path: .anechoic_anechoic
---
## Summary

Declare anechoic

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Project

declare_entity(
    entity_name='anechoic',
    instance=Project(
        id='CA-SU-00',
        name='anechoic',
        structural_level=0,
    ),
)
```
