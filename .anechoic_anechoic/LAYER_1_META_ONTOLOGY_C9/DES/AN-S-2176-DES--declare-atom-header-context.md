---
identity:
  atom_id: AN-S-2176
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T00:27:07.579107+00:00'
---


## Summary

Declare Atom.Header.Context

## Claim

### Prose Claim

A Role-specific group uses the Role name. A Form-specific group is nested in its Role-specific group and uses the Form name.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(entity_name="Context", relation_name="IS_PROPERTY_OF", base_path="Atom.Header", property_occurrence_cardinality=1, value_cardinality=0, dependent_property_cardinality=Cardinality(minimum=5, maximum=7), allowed_dependent_property_names=("Container", "Role", "Form", "Label", "Topics", "Tier", "Plan", "Concern"), ordered_dependent_property_pairs=(("Container", "Role"), ("Role", "Form"), ("Form", "Label"), ("Label", "Topics"), ("Topics", "Tier")))
```
