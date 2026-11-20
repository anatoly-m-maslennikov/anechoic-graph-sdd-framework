---
identity:
  atom_id: AN-S-2012
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare Atom/(.Role := Method)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Method(Atom):
    pass

declare_entity(
    entity_class=Method,
    entity_name='Method',
    qualification_property_path='Atom.Header.Context.Role',
    classifications={'Role Order Number': 5},
)
```

## Semantics

A Method specifies domain and engineering designs, mechanisms or working approaches for achieving required results.
