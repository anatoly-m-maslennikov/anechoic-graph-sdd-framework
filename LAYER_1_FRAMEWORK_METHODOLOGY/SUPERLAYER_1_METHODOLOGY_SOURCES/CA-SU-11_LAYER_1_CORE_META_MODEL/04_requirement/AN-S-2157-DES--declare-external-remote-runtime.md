---
identity:
  atom_id: AN-S-2157
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

Declare External Remote Runtime

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Runtime

class ExternalRemoteRuntime(Runtime):
    pass

declare_entity(
    entity_class=ExternalRemoteRuntime,
    entity_name='External Remote Runtime',
)
```

## Semantics

An External Remote Runtime is a Runtime external to our application on a machine other than the Operator’s.
