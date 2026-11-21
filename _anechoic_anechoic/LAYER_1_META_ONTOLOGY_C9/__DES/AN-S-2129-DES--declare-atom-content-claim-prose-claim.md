---
atom_family: SPEC
atom_id: AN-S-2129
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-12T19:13:08.274065+00:00'
---

## Summary

Declare Atom.Content.Claim.Prose Claim

## Claim

### Prose Claim

Prose Claim is a child Property of Claim. Its value is ordinary Markdown; headings within that value are not Properties unless an applicable declaration admits them.
### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Requirement, Method, Evaluation, Delivery

declare_entity(
    entity_name="Prose Claim",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Content.Claim",
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
    applies_to_entity_classes=(Requirement, Method, Evaluation, Delivery),
)
```
