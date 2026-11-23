---
atom_family: SPEC
atom_id: AN-S-2123
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T18:49:35.824257+00:00'
---
## Summary

Declare Projection/(.Form := Entity Definition and Active Subject Coverage)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class EntityDefinitionAndActiveSubjectCoverage(Projection):
    pass

declare_entity(entity_class=EntityDefinitionAndActiveSubjectCoverage, entity_name='Entity Definition and Active Subject Coverage', qualification_property_path="Projection.Form")
```
