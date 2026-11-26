---
atom_family: SPEC
atom_id: AN-S-2193
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: "2026-11-25T19:35:30.469831+00:00"
---
## Summary

Declare Atom.Header.Label

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Label",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header.Context",
    value_format=str,
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
    fallback_property_name="Form",
)
```
