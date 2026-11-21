---
atom_family: SPEC
atom_id: AN-S-2283
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:39:49.768039+00:00'
---
## Summary

Declare Method Eng Standard Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Method

class MethodEngStandard(Method):
    pass

declare_entity(
    entity_class=MethodEngStandard,
    entity_name='Eng Standard',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

An Eng Standard applies directly to implementation within its owning Scope Unit and descendant Scope Units where its Claim applies.