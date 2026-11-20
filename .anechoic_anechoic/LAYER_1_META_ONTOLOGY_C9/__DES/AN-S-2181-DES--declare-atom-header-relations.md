---
atom_family: SPEC
atom_id: AN-S-2181
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-20T16:33:53.377856+00:00'
---
## Summary

Declare Atom.Header.Relations

## Claim

### Prose Claim

Each child name is the canonical name of a declared Relation. Each child has one or more Atom references in the form that its Relation permits. Use base Atom IDs when the Relation specifies no other form. A present Relations group has at least one child.

The replacement Atom stores IS_REPLACEMENT_FOR with its predecessor Atom IDs.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Relations",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom.Header",
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=1, maximum=None),
    dependent_property_name_format=str,
    dependent_property_value_format=str,
    dependent_property_value_cardinality=Cardinality(minimum=1, maximum=None),
)
```
