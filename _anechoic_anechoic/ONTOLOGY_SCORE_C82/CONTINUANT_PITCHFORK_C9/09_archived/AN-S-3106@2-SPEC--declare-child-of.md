---
atom_family: SPEC
atom_id: AN-S-3106
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: '2026-11-21T12:25:59+00:00'
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

## Classifications

| Relation | Transitive | Functional |
| --- | --- | --- |
| `CHILD_OF` | no | yes |
| `CHILDREN` | no | no |

`CHILD_OF` identifies an immediate parent. AN-S-3148 gives each Component one parent, and AN-S-3146 gives Project zero parents. `CHILDREN` can return multiple immediate children.
