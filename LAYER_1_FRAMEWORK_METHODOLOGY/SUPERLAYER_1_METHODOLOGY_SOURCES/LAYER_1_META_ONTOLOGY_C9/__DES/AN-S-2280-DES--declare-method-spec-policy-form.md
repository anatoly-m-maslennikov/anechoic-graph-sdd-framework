---
atom_family: SPEC
atom_id: AN-S-2280
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:39:37.258710+00:00'
---
## Summary

Declare Method Spec Policy Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Method

class MethodSpecPolicy(Method):
    pass

declare_entity(
    entity_class=MethodSpecPolicy,
    entity_name='Spec Policy',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Spec Policy governs how to write and review Atoms of the same Role whose main subject is its own main subject or a descendant.