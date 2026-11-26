---
atom_family: SPEC
atom_id: AN-S-2125
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 9
  updated_at: "2026-11-25T19:46:35.615401+00:00"
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
