---
atom_family: SPEC
atom_id: AN-S-2182
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 7
  updated_at: '2026-11-13T01:11:40.238494+00:00'
---
## Summary

Declare Atom.Content

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Requirement, Method, Evaluation, Delivery
declare_entity(entity_name="Content", relation_name="IS_PROPERTY_OF", base_path="Atom",
    property_occurrence_cardinality=1, value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=None), dependent_property_name_format=str,
    recursive_dependent_property_cardinality=Cardinality(minimum=0, maximum=None),
    recursive_dependent_property_name_format=str, recursive_dependent_property_value_format="markdown",
    ordered_dependent_property_roles=(Requirement, Method, Evaluation, Delivery),
    ordered_dependent_property_pairs=(("Summary", "Claim"), ("Claim", "Semantics"), ("Semantics", "Details")))
```