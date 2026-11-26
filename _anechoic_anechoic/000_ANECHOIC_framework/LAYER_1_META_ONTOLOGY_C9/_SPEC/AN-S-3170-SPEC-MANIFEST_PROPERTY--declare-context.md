---
atom_family: SPEC
atom_id: AN-S-3170
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 4
  updated_at: "2026-11-25T16:00:38.050318+00:00"
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
