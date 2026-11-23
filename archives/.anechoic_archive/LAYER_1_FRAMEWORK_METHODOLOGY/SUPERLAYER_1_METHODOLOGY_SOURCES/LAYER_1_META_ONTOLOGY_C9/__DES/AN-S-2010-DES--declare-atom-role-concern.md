---
atom_family: SPEC
atom_id: AN-S-2010
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Atom/(.Role := Concern)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Concern(Atom):
    pass

declare_entity(entity_class=Concern, entity_name='Concern', qualification_property_path="Atom.Header.Context.Role", classifications={"Role Order Number": 1})
```

## Semantics

A Concern identifies a question, conflict, or problem.
