---
atom_family: SPEC
atom_id: AN-S-2131
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T19:20:12.374663+00:00'
---

## Summary

Declare Atom/(.Header.Context.Role := Concern).Header.Context.Concern

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Concern

declare_entity(
    entity_name='Concern',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.Context',
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=1,
    allowed_dependent_property_names=('Priority',),
    applies_to_entity_classes=(Concern,),
)
```
