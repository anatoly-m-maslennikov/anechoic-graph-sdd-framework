---
atom_family: SPEC
atom_id: AN-S-2116
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:46:52.789021+00:00"
---
## Summary

Declare Projection/(.Form := Map)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class Map(Projection):
    pass

declare_entity(entity_class=Map, entity_name='Map', qualification_property_path="Projection.Form")
```
