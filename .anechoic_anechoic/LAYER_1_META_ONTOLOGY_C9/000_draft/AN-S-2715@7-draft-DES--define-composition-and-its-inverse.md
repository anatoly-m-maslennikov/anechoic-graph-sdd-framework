---
identity:
  atom_id: AN-S-2715
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 7
  updated_at: '2026-11-13T08:49:23.301697+00:00'
---
## Summary

Define composition and its inverse

## Claim

### Prose Claim

IS_CONTAINED_BY relates a contained declared Entity or instance to its immediate Container. The Target has classification `Container = yes`. Containment does not imply narrowing or inheritance. CONTAINS is its derived inverse: its Host and Target are the direct Target and Host, respectively. Store the direct fact once.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_CONTAINED_BY",
    inverse_alias="CONTAINS",
    source_endpoint={"level": "model_entities_or_instances"},
    target_endpoint={"level": "model_entities_or_instances"},
    written_alias="+>",
    reverse_written_alias="<+",
)
```

