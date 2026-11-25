---
atom_family: SPEC
atom_id: AN-S-2118
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:43:34.767784+00:00"
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
