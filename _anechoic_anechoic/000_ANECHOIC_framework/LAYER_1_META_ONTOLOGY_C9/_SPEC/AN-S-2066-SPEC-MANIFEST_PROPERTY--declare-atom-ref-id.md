---
atom_family: SPEC
atom_id: AN-S-2066
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "active"
  version: 9
  updated_at: "2026-11-25T16:00:37.647080+00:00"
---

## Summary

Declare Atom.Ref ID

## Claim

### Prose Claim

Ref ID is computed on read and is not persisted.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property2066(Property):
    name = 'Ref ID'
    bearer = Atom
    property.value.derived_from = ('Header.Atom ID', 'Header.State.Version', 'Header.State.Status')
    property.cardinality = 1
    property.value.cardinality = 1
    property.value.format = str
```
