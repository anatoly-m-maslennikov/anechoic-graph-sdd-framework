---
atom_family: SPEC
atom_id: AN-S-2119
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T18:49:25.879498+00:00'
---
## Summary

Declare Projection/(.Form := Primary Entities with Direct Properties)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class PrimaryEntitiesWithDirectProperties(Projection):
    pass

declare_entity(entity_class=PrimaryEntitiesWithDirectProperties, entity_name='Primary Entities with Direct Properties', qualification_property_path="Projection.Form")
```
