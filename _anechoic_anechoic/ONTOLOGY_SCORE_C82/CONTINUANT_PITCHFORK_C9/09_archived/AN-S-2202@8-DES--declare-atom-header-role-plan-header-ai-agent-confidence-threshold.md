---
atom_family: SPEC
atom_id: AN-S-2202
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 8
  updated_at: "2026-11-25T23:03:10.673704+00:00"
---
## Summary

Declare Atom/(.Header.Role := Plan).Header.AI Agent Confidence Threshold

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="AI Agent Confidence Threshold",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role:=Plan).Header.Context.Plan",
    value_format=int,
    value_cardinality=Cardinality(minimum=0, maximum=1),
    minimum_value=0,
    maximum_value=100,
    dependent_property_cardinality=0,
    fallback_chain=(
        {
            "lookup_relation": "IS_CONTAINED_BY",
            "lookup_property": "Atom/(.Header.Context.Role:=Plan).Header.Context.Plan.AI Agent Confidence Threshold",
        },
        {
            "project_entity": "Project",
            "project_property": "Project.Settings.AI Agent Confidence Threshold",
        },
    ),
)
```
