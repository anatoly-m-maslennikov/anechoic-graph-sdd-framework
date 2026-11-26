---
atom_family: SPEC
atom_id: AN-S-2058
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:43:33.486002+00:00"
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
