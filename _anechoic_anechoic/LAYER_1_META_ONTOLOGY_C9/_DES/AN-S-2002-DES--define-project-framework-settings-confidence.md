---
atom_family: SPEC
atom_id: AN-S-2002
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 17
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Project.Framework Settings.Confidence

## Claim

### Prose Claim


the Confidence grouping in the Project's Framework Settings.



### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Confidence',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=2),
    allowed_dependent_property_names=('Necessary Information Threshold', 'Semantic Resolution Threshold'),
    dependent_property_value_format='int',
)
```

## Details

Evidence: CA-R-1652 defines the necessary-information threshold default; CA-R-380 defines the semantic-resolution threshold default. These define the child settings, not the parent grouping. Candidate #6 decision 8 retains Settings as the default source, and decision 18 distinguishes Project settings from the framework's name. This grouping adds no threshold, override layer or mandatory value. Concrete ANECHOIC setting definitions belong in Project Configuration.
