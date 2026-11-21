---
atom_family: SPEC
atom_id: AN-S-2173
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: draft
  version: 7
  updated_at: '2026-11-13T14:59:14.324891+00:00'
---

## Summary

Declare Atom.Content.Claim.Formal Claim

## Claim

### Prose Claim

Formal Claim is a child Property of Claim. Its value contains one fenced formal expression. Use Python for the Formal Claim.
### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Formal Claim",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Content.Claim",
    applies_to_entity_classes=("Requirement", "Method", "Evaluation", "Delivery"),
    value_format="markdown",
    value_cardinality=Cardinality(minimum=0, maximum=1),
    dependent_property_cardinality=0,
)
```
