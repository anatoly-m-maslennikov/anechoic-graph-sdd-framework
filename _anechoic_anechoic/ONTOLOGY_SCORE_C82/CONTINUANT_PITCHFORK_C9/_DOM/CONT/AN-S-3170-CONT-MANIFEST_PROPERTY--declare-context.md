---
atom_family: SPEC
atom_id: AN-S-3170
concern:
  subject: Context
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:33.662127+00:00"
---

## Summary

Declare Context

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Property3170(Property):
    name = 'Context'
    bearer = Atom.Header
    property.dependent_property.name.allowed = ('Template', 'Label', 'Lens')
    property.dependent_property.ordered_pairs = (('Template', 'Label'), ('Label', 'Lens'))
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 0
    property.value.format = object
```
