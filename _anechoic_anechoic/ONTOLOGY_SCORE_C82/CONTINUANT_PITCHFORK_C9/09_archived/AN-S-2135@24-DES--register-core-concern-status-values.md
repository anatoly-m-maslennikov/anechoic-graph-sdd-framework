---
atom_family: SPEC
atom_id: AN-S-2135
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: "archived"
  version: 24
  updated_at: "2026-11-25T19:46:38.762732+00:00"
---
## Summary

Register Core Concern Status Values

## Claim

### Prose Claim


the Core Concern Status model.


the Core Concern Status model **must** inherit the allowed values of Atom.Header.Status and add (Resolved, Canceled).

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Concern

declare_entity(
    entity_name='Status',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.State',
    allowed_values=('Resolved', 'Canceled'),
    status_order_numbers={'Resolved': 21},
    applies_to_entity_classes=(Concern,),
)
```
