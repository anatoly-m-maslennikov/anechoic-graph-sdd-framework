---
atom_family: SPEC
atom_id: AN-S-2179
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 8
  updated_at: '2026-11-13T00:27:09.632965+00:00'
---

## Summary

Declare Atom.Content.Claim

## Claim

### Prose Claim

A complete ordinary RMED Claim has at least one of Formal Claim and Prose Claim. Sibling names are unique. Formal Claim uses the fenced language admitted by its declaration. Prose Claim contains ordinary Markdown. A Markdown heading inside Prose Claim is part of its value, unless an applicable declaration expressly declares it as a child Property.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Requirement, Method, Evaluation, Delivery

declare_entity(entity_name="Claim", relation_name="IS_PROPERTY_OF", base_path="Atom.Content", property_occurrence_cardinality=1, value_cardinality=0, dependent_property_cardinality=Cardinality(minimum=1, maximum=2), dependent_property_name_format=str, allowed_dependent_property_names=("Formal Claim", "Prose Claim"), ordered_dependent_property_pairs=(("Prose Claim", "Formal Claim"),), applies_to_entity_classes=(Requirement, Method, Evaluation, Delivery))
```
