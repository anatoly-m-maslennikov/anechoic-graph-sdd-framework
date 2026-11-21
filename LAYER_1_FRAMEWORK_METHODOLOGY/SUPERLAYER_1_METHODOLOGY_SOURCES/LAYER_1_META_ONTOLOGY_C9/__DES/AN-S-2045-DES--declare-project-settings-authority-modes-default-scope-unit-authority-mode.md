---
atom_family: SPEC
atom_id: AN-S-2045
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T17:23:54+00:00'
---

## Summary

Declare Project.Settings.Authority Modes.Default Scope Unit Authority Mode

## Claim

### Prose Claim


The permitted values are `strict` and `casual`. The effective selection follows the applicable authority-mode resolution.

### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Default Scope Unit Authority Mode',
    relation_name='IS_PROPERTY_OF',
    base_path='Project.Settings.Authority Modes',
    property_occurrence_cardinality=1,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```

