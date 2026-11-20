---
identity:
  atom_id: AN-S-2058
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Declare Projection/(.Form := Catalog)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class Catalog(Projection):
    pass

declare_entity(
    entity_class=Catalog,
    entity_name='Catalog',
    qualification_property_path='Projection.Form',
)
```
