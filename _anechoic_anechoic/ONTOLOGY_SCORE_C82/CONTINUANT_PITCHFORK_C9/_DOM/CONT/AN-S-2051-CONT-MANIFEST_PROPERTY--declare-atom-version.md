---
atom_family: SPEC
atom_id: AN-S-2051
concern:
  subject: Version
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
  version: 8
  updated_at: "2026-11-26T15:52:30.545483+00:00"
---
## Summary

Declare Atom.Version

## Semantics

Versions increase across successive revisions of the same Atom ID.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property2051(Property):
    name = 'Version'
    bearer = Atom.Header.State
    property.value.minimum = 1
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = int
```
