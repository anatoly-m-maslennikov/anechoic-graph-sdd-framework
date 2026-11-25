---
atom_family: SPEC
atom_id: AN-S-2284
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:39:56.937089+00:00'
---
## Summary

Declare Evaluation Eng Standard Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Evaluation

class EvaluationEngStandard(Evaluation):
    pass

declare_entity(
    entity_class=EvaluationEngStandard,
    entity_name='Eng Standard',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

An Eng Standard applies directly to implementation within its owning Scope Unit and descendant Scope Units where its Claim applies.