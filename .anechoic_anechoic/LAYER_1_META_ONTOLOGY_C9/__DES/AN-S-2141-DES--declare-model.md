---
atom_family: SPEC
atom_id: AN-S-2141
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T20:21:33.885135+00:00'
---
## Summary

Declare MODEL

## Claim

### Prose Claim



- A local MODEL inherits ANECHOIC's MODEL.
- MODEL inheritance is distinct from Node narrowing.
- Local overrides replace matching inherited rules in the local MODEL.
- Local overrides preserve the base MODEL's rules.
- Unmodified inherited Declarations are reused.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Node

class Model(Node):
    pass

declare_entity(
    entity_class=Model,
    entity_name='MODEL',
    model_relation_constraints={"IS_PROPERTY_OF": {"targets_per_source": 0}},
    classifications={"Container": "yes"},
)
```

## Semantics

MODEL declares Node kinds, Relations, Properties, and rules.
