---
atom_id: CA-R-2257
ref_id: CA-R-2257
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Format/scalar
tier: 1
status: active
version: 8
updated_at: '2026-11-13T22:57:39.635646+00:00'
carrier_destination:
  file:
    name: CA-R-2257-CORE_META_MODEL-DECLARATION--define-scalar-value-format.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Define scalar Value Format

## Claim

### Prose Claim


The scalar Value Format admits a direct primitive value, including string,
numeric, Boolean, date/time and null values supported by the declared Carrier.
Sequences and mappings remain Carrier structures: sequence members are counted
individually, while child mapping keys are not direct values of their parent.
Specific Formats can restrict this broad domain.



### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import ValueFormat

class ScalarValueFormat(ValueFormat):
    pass

declare_entity(entity_name='scalar', entity_class=ScalarValueFormat)
```
