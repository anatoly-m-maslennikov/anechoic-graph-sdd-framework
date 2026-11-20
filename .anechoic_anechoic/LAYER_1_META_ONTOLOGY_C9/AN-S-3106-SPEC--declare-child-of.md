---
identity:
  atom_id: AN-S-3106
context:
  container:
    component: C9
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Declare CHILD_OF

## Claim scope

MODEL//ANECHOIC <+ Relation//CHILD_OF

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="CHILD_OF",
    inverse_alias="CHILDREN",
    source_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Component",)},
    target_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Component",)},
    acyclic=True,
)
```
