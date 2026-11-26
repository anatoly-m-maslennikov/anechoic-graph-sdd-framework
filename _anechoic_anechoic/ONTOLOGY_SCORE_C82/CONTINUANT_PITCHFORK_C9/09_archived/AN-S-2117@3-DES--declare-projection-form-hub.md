---
atom_family: SPEC
atom_id: AN-S-2117
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:43:34.075408+00:00"
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
