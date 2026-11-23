---
atom_family: SPEC
atom_id: AN-S-2168
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T23:10:08.677592+00:00'
---

## Summary

Declare Step.Fixed Parameters

## Claim

### Prose Claim

A Step may declare fixed parameter values for its invocation. A fixed value is one permitted source of a binding.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity

declare_entity(entity_name='Fixed Parameters', relation_name="IS_PROPERTY_OF", base_path='Atom/(.Header.Context.Role:=Operations)/Step')
```
