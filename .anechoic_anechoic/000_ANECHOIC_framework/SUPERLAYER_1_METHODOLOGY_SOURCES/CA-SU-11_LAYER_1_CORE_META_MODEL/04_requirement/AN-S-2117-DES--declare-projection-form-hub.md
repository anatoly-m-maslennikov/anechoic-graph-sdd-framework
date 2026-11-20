---
atom_family: SPEC
atom_id: AN-S-2117
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T18:49:20.840540+00:00'
---
## Summary

Declare Projection/(.Form := Hub)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class Hub(Projection):
    pass

declare_entity(entity_class=Hub, entity_name='Hub', qualification_property_path="Projection.Form")
```
