---
atom_family: SPEC
atom_id: AN-S-2133
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T19:19:39.079406+00:00'
---
## Summary

Declare Named Selection

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Continuant

class NamedSelection(Continuant):
    pass

declare_entity(
    entity_class=NamedSelection,
    entity_name="Named Selection",
    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},
)
```

## Semantics

A Named Selection names criteria for choosing members. Selected members retain their identity.
