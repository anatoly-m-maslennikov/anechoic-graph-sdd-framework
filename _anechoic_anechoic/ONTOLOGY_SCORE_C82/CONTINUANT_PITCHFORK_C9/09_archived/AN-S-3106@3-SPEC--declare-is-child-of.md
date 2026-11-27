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
  version: 3
  updated_at: '2026-11-21T13:03:17+00:00'
---

## Summary

Declare IS_CHILD_OF

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_CHILD_OF

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_CHILD_OF",
    inverse_alias="HAS_CHILDREN",
    source_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Component",)},
    target_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Component",)},
    acyclic=True,
    classifications={"Transitive": "no", "Functional": "yes"},
    inverse_classifications={"Transitive": "no", "Functional": "no"},
)
```

## Semantics

A Component is a child of its immediate parent. Each Component has at
most one parent, and a Project has zero. Derive each HAS_CHILDREN link
by reversing one IS_CHILD_OF fact.
