---
atom_family: SPEC
atom_id: AN-S-2051
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-26T15:54:01.786874+00:00"
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
