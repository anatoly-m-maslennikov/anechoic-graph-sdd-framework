---
atom_family: SPEC
atom_id: AN-S-2122
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: '2026-11-12T18:49:33.352385+00:00'
---
## Summary

Declare Projection/(.Form := Subjects without Requirement Declarations)

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection

class SubjectsWithoutRequirementDeclarations(Projection):
    pass

declare_entity(entity_class=SubjectsWithoutRequirementDeclarations, entity_name='Subjects without Requirement Declarations', qualification_property_path="Projection.Form")
```
