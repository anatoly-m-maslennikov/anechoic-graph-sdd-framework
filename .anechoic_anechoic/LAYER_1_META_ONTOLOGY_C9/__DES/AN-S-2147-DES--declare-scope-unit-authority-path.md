---
atom_family: SPEC
atom_id: AN-S-2147
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T22:04:01.428900+00:00'
---
## Summary

Declare Scope Unit Authority Path

## Claim

### Prose Claim

Authority is the Project-root-relative path to the Scope Unit’s Atom folder in the Project’s `.anechoic_<project name>` tree. Use the actual folder names.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Authority",
    relation_name="IS_PROPERTY_OF",
    base_path="Scope Unit.Paths",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
