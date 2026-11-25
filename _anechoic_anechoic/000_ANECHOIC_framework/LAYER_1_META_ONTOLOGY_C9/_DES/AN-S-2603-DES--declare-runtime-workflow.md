---
atom_family: SPEC
atom_id: AN-S-2603
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 4
  updated_at: '2026-11-13T03:39:08.573175+00:00'
---

## Summary

Declare Runtime Workflow

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name="Purpose",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom/(.Header.Context.Role := Operations)/Workflow",
    allowed_values=('Runtime',),
)
```

## Semantics

A Runtime Workflow is a Workflow whose Purpose is Runtime: it provides behavior through a Project's delivered result during its operation. In ANECHOIC, examples include Create Draft, Promote Draft and Archive Atom.

It inherits Workflow's shared recursive Step and Action model. Purpose describes use relative to a Project and does not change the canonical definition's owning Scope Unit.
