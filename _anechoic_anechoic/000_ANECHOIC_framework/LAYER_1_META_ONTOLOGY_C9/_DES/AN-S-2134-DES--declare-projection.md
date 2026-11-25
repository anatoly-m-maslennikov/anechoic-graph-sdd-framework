---
atom_family: SPEC
atom_id: AN-S-2134
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T19:19:43.082639+00:00'
---
## Summary

Declare Projection

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Continuant

class Projection(Continuant):
    pass

declare_entity(
    entity_class=Projection,
    entity_name="Projection",
    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},
)
```

## Semantics

A Projection is a derived view of source Atoms. It does not establish or override their Claims.
