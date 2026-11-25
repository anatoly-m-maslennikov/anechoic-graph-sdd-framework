---
atom_family: SPEC
atom_id: AN-S-2695
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: active
  version: 9
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Define IS_EXECUTION_OF Relation

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_EXECUTION_OF",
    inverse_alias="HAS_EXECUTION",
    endpoint_pairs=(
        {"source_endpoint": {"level": "instances", "entity_paths": ("Workflow Run",)},
         "target_endpoint": {"level": "instances", "entity_paths": ("Atom/(.Header.Context.Role:=Operations)/Workflow",)}},
        {"source_endpoint": {"level": "instances", "entity_paths": ("Step Run",)},
         "target_endpoint": {"level": "instances", "entity_paths": ("Atom/(.Header.Context.Role:=Operations)/Step",)}},
        {"source_endpoint": {"level": "instances", "entity_paths": ("Action Run",)},
         "target_endpoint": {"level": "instances", "entity_paths": ("Atom/(.Header.Context.Role:=Operations)/Action",)}},
    ),
)
```


## Semantics

IS_EXECUTION_OF relates an actual Workflow Run, Step Run or Action Run to the corresponding reusable definition it executes.
