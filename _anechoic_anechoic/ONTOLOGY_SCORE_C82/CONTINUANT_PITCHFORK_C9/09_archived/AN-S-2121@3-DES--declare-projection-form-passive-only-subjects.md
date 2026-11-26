---
atom_family: SPEC
atom_id: AN-S-2121
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T22:43:36.571442+00:00"
---
## Summary

Declare Projection/(.Form := Passive Only Subjects)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class PassiveOnlySubjects(Projection):
    pass

declare_entity(entity_class=PassiveOnlySubjects, entity_name='Passive Only Subjects', qualification_property_path="Projection.Form")
```
