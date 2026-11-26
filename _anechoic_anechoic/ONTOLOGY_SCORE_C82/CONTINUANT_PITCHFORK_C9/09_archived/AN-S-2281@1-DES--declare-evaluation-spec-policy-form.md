---
atom_family: SPEC
atom_id: AN-S-2281
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T22:48:45.106206+00:00"
---
## Summary

Declare Evaluation Spec Policy Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Evaluation

class EvaluationSpecPolicy(Evaluation):
    pass

declare_entity(
    entity_class=EvaluationSpecPolicy,
    entity_name='Spec Policy',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Spec Policy governs how to write and review Atoms of the same Role whose main subject is its own main subject or a descendant.