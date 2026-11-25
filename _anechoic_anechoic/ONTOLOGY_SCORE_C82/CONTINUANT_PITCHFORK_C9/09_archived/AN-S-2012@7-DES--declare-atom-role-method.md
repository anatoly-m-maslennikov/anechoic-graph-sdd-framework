---
atom_family: SPEC
atom_id: AN-S-2012
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-25T21:25:21.203717+00:00"
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
