---
atom_family: SPEC
atom_id: AN-S-2178
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 6
  updated_at: "2026-11-26T15:54:01.841453+00:00"
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
