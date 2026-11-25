---
atom_family: SPEC
atom_id: AN-S-2120
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:43:35.852825+00:00"
---
## Summary

Declare Projection/(.Form := Primary Entities with Inherited Property Contracts)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class PrimaryEntitiesWithInheritedPropertyContracts(Projection):
    pass

declare_entity(entity_class=PrimaryEntitiesWithInheritedPropertyContracts, entity_name='Primary Entities with Inherited Property Contracts', qualification_property_path="Projection.Form")
```
