---
atom_family: SPEC
atom_id: AN-S-2004
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 16
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Define Project.Framework Settings.Interaction

## Claim

### Prose Claim


the Interaction grouping in the Project's Framework Settings.



### Formal Claim

```python
# model
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name='Interaction',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=1,
    allowed_dependent_property_names=('Reporting Mode',),
)
```

## Details

Evidence: CA-R-1628 defines reporting-mode values; CA-R-1439 limits effects to presentation; CA-R-1440 preserves mandatory information. These define the child setting and its constraints, not the parent grouping. Candidate #6 keeps concrete ANECHOIC mechanisms in Project Configuration. This grouping adds no authorization, workflow, validation or safety behavior.
