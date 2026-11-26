---
atom_family: SPEC
atom_id: AN-S-2001
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 16
  updated_at: "2026-11-25T22:55:44.624683+00:00"
---
## Summary

Define Project.Framework Settings.Code-Root Locators

## Claim

### Prose Claim


the code-root references in the Project's Framework Settings.



### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Code-Root Locators',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=Cardinality(minimum=1, maximum=None),
    value_format='str',
    dependent_property_cardinality=0,
)
```

## Details

Evidence: CA-D-371 requires code-root locators in Framework Settings. Candidate #6 keeps concrete ANECHOIC mechanisms in Project Configuration. This definition adds no discovery procedure, new root or locator count.
