---
atom_family: SPEC
atom_id: AN-S-2158
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

Declare Session

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ExternalRemoteRuntime

class Session(ExternalRemoteRuntime):
    pass

declare_entity(
    entity_class=Session,
    entity_name='Session',
)
```

## Semantics

A Session is an External Remote Runtime for ongoing interaction.
