---
atom_family: SPEC
atom_id: AN-S-2274
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

Declare Operations Decision Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Operations

class OperationsDecision(Operations):
    pass

declare_entity(
    entity_class=OperationsDecision,
    entity_name='Decision',
    qualification_property_path='Atom.Header.Context.Form',
)
```

## Semantics

A Decision records a particular local choice. Applicable governing constraints continue to apply.
