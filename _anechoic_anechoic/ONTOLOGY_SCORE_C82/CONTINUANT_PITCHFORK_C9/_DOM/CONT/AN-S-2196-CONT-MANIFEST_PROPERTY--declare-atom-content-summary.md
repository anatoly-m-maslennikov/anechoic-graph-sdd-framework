---
atom_family: SPEC
atom_id: AN-S-2196
concern:
  subject: Summary
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Content
  relation: is_property_of
container:
  component: C9
tier: 3
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 9
  updated_at: "2026-11-26T15:52:30.806263+00:00"
---
## Summary

Declare Atom.Content.Summary

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Summary(Property):
    bearer = Atom.Content
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
    property.dependent_property.cardinality = 0
```

## Semantics

The Summary helps readers find and recognize the Atom. It has no authority or revision of its own. Revisions of the same Atom preserve its Summary under AN-S-1604.

