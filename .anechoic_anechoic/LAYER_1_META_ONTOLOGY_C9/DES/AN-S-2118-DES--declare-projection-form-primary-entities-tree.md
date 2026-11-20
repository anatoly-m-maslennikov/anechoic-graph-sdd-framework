---
identity:
  atom_id: AN-S-2118
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T18:49:23.370786+00:00'
---
## Summary

Declare Projection/(.Form := Primary Entities Tree)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class PrimaryEntitiesTree(Projection):
    pass

declare_entity(entity_class=PrimaryEntitiesTree, entity_name='Primary Entities Tree', qualification_property_path="Projection.Form")
```
