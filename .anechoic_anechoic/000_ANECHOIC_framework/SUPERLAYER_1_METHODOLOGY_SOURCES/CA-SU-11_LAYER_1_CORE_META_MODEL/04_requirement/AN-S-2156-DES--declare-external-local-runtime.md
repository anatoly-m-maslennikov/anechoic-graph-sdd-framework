---
identity:
  atom_id: AN-S-2156
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Declare External Local Runtime

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Runtime

class ExternalLocalRuntime(Runtime):
    pass

declare_entity(
    entity_class=ExternalLocalRuntime,
    entity_name='External Local Runtime',
)
```

## Semantics

An External Local Runtime is a Runtime external to our application on the Operator’s machine.
