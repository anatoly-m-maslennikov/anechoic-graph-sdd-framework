---
atom_family: SPEC
atom_id: AN-S-2172
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-12T23:58:00.042337+00:00'
---

## Summary

Declare Atom/(.Role := Operations)/Action.Execution Kind

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Execution Kind",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role := Operations)/Action",
    property_occurrence_cardinality=1,
    value_format=str,
    value_cardinality=1,
    dependent_property_cardinality=0,
    allowed_values=("Programmatic", "Agentic"),
)
```

