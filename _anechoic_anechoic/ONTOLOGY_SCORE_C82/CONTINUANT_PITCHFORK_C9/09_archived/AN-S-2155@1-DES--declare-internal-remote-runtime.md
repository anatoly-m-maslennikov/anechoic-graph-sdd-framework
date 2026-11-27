---
atom_family: SPEC
atom_id: AN-S-2155
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T09:25:51.969207+00:00"
---
## Summary

Declare Internal Remote Runtime

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Runtime

class InternalRemoteRuntime(Runtime):
    pass

declare_entity(
    entity_class=InternalRemoteRuntime,
    entity_name='Internal Remote Runtime',
)
```

## Semantics

An Internal Remote Runtime is a Runtime of our application on a machine other than the Operator’s.
