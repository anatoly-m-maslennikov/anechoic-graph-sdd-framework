---
atom_family: SPEC
atom_id: AN-S-2182
concern:
  subject: Content
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom
  relation: is_property_of
container:
  component: C9
tier: 3
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 13
  updated_at: "2026-11-26T15:52:30.774131+00:00"
---

## Summary

Declare Atom.Content

## Formal Manifest

```python anechoic-edsl
from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Content(Property):
    bearer = Atom
    property.cardinality = 1
    property.value.cardinality = 0
    property.dependent_property.cardinality = Cardinality(minimum=0, maximum=None)
    property.dependent_property.name.format = str
    property.dependent_property.recursive.cardinality = Cardinality(minimum=0, maximum=None)
    property.dependent_property.recursive.name.format = str
    property.dependent_property.recursive.value.format = "markdown"
```

## Semantics

Atom Content expresses the Atom's contribution and provides the context needed to understand it.
