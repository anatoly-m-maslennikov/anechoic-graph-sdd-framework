---
identity:
  atom_id: AN-S-2009
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 6
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Declare Atom.Content.Details

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Delivery, Evaluation, Method, Requirement

declare_entity(
    entity_name='Details',
    relation_name='IS_PROPERTY_OF',
    base_path='Atom.Content',
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=Cardinality(minimum=0, maximum=None),
    dependent_property_name_format=str,
    applies_to_entity_classes=(Requirement, Method, Evaluation, Delivery),
)
```

