---
atom_family: SPEC
atom_id: AN-S-2125
concern:
  subject: Status
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom.Header.State
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 10
  updated_at: "2026-11-26T15:52:30.658061+00:00"
---
## Summary

Declare Atom.Status

## Semantics

Status records an Atom revision's lifecycle state. The Atom Family supplies its allowed values. AN-S-3160 defines the Carrier representation.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property2125(Property):
    name = 'Status'
    bearer = Atom.Header.State
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
