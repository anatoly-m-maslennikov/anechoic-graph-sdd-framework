---
atom_family: SPEC
atom_id: AN-S-2156
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T09:25:52.436943+00:00"
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
