---
atom_family: SPEC
atom_id: AN-S-2272
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---

## Summary

Declare Evaluation Decision Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Evaluation

class EvaluationDecision(Evaluation):
    pass

declare_entity(
    entity_class=EvaluationDecision,
    entity_name='Decision',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Decision records a particular local choice. Applicable governing constraints continue to apply.
