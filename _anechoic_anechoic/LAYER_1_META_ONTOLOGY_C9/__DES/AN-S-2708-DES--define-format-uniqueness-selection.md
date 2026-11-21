---
atom_family: SPEC
atom_id: AN-S-2708
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-12T21:16:52.698794+00:00'
---
## Summary

Define Format Uniqueness Selection

## Claim

### Prose Claim


Format Uniqueness Selection identifies the comparison population for a
Property uniqueness check. It is optional and does not itself impose
uniqueness. It does not define a notation.



### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Uniqueness Selection",
    relation_name="IS_PROPERTY_OF",
    base_path="Format",
    value_format=str,
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```
