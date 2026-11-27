---
atom_family: SPEC
atom_id: AN-S-2178
concern:
  subject: State
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
  version: 7
  updated_at: "2026-11-26T15:52:30.732548+00:00"
---


## Summary

Declare Atom.State

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property2178(Property):
    name = 'State'
    bearer = Atom.Header
    property.dependent_property.name.allowed = ('Status', 'Version', 'Updated At')
    property.dependent_property.ordered_pairs = (('Status', 'Version'), ('Version', 'Updated At'))
    property.cardinality = 1
    property.value.cardinality = 0
    property.value.format = object
```
