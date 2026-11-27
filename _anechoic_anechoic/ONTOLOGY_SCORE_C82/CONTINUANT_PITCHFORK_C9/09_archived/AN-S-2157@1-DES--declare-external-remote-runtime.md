---
atom_family: SPEC
atom_id: AN-S-2157
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T09:25:52.865531+00:00"
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
