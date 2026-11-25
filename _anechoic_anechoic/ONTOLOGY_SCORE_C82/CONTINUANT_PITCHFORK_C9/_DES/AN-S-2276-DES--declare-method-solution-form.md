---
atom_family: SPEC
atom_id: AN-S-2276
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T20:07:31.109779+00:00'
---

## Summary

Declare Method Solution Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Method

class MethodSolution(Method):
    pass

declare_entity(
    entity_class=MethodSolution,
    entity_name='Solution',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Solution specifies the contribution that realizes a Scope Unit’s responsibility across the unit and its descendants. Its Role identifies the contribution.
