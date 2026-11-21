---
atom_family: SPEC
atom_id: AN-S-2013
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare Atom/(.Role := Evaluation)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class Evaluation(Atom):
    pass

declare_entity(
    entity_class=Evaluation,
    entity_name='Evaluation',
    qualification_property_path='Atom.Header.Context.Role',
    classifications={'Role Order Number': 6},
)
```

## Semantics

An Evaluation specifies falsifiable checks and how their evidence is interpreted to determine whether required results are achieved.
