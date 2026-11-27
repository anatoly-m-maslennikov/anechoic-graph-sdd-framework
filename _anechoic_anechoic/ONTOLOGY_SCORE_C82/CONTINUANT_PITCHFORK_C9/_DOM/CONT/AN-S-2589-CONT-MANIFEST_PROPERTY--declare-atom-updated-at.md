---
atom_family: SPEC
atom_id: AN-S-2589
concern:
  subject: Updated At
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.State
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 9
  updated_at: "2026-11-26T15:52:30.894636+00:00"
---
## Summary

Declare Atom.Updated At

## Semantics

Updated At records when this Atom revision was created or last edited. The date-time identifies one instant and includes its UTC offset.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from datetime import datetime

class Property2589(Property):
    name = 'Updated At'
    bearer = Atom.Header.State
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = datetime
```
