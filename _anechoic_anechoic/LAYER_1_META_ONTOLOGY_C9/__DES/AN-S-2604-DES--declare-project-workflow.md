---
atom_family: SPEC
atom_id: AN-S-2604
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T03:39:10.851210+00:00'
---

## Summary

Declare Project Workflow

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Purpose",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role := Operations)/Workflow",
    allowed_values=('Project',),
)
```

## Semantics

A Project Workflow is a Workflow whose Purpose is Project: it develops, validates, maintains or releases a Project's result. Examples include Implementation, Local Release and Public Release.

It inherits Workflow's shared recursive Step and Action model. Purpose describes use relative to a Project and does not change the canonical definition's owning Scope Unit.
