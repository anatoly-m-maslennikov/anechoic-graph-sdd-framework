---
atom_family: SPEC
atom_id: AN-S-2132
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T19:32:46.193364+00:00"
---

## Summary

Declare Atom/(.Header.Context.Role := Plan).Header.Context.Plan

## Claim

### Prose Claim

The Plan group is present only for an Atom with Plan Role and is omitted when it would contain no declared Property.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity
from anechoic.model import Plan

declare_entity(
    entity_name='Plan',
    relation_name="IS_PROPERTY_OF",
    base_path='Atom.Header.Context',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=1, maximum=2),
    allowed_dependent_property_names=('Work Sequence Number', 'AI Agent Confidence Threshold'),
    applies_to_entity_classes=(Plan,),
)
```
