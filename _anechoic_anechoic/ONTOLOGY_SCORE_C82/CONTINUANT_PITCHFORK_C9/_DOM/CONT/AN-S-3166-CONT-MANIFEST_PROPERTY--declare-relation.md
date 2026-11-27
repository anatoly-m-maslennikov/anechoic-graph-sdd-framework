---
atom_family: SPEC
atom_id: AN-S-3166
concern:
  subject: Relation
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.Concern
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
  updated_at: "2026-11-26T15:52:33.548777+00:00"
---

## Summary

Declare Relation

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property
from anechoic.formal_claims import Cardinality

class Property3166(Property):
    name = 'Relation'
    bearer = Atom.Header.Concern
    field_options = {'default': None, 'kw_only': True}
    property.cardinality = Cardinality(minimum=0, maximum=1)
    property.value.cardinality = 1
    property.value.format = str | None
```
