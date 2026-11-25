---
atom_family: SPEC
atom_id: AN-S-2127
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T19:06:44.073009+00:00'
---
## Summary

Declare Atom.Header.Tier

## Claim

### Prose Claim

Atom.Header.Tier stores one integer value and an optional Tier Label; the Formal Claim defines their representation.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Tier",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context",
    property_occurrence_cardinality=1,
    value_format=int,
    value_cardinality=1,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=1),
    allowed_dependent_property_names=("Label",),
    minimum_value=-1,
)
```
