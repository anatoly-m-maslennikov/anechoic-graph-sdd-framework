---
atom_family: SPEC
atom_id: AN-S-2154
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: 2026-11-04 16:07:35 +0400
---
## Summary

Declare Internal Local Runtime

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Runtime

class InternalLocalRuntime(Runtime):
    pass

declare_entity(
    entity_class=InternalLocalRuntime,
    entity_name='Internal Local Runtime',
)
```

## Semantics

An Internal Local Runtime is a Runtime of our application on the Operator’s machine.
