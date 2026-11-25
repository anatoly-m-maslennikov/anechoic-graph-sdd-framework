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
  version: 8
  updated_at: "2026-11-25T16:00:37.654070+00:00"
---
## Summary

Declare Atom.Status

## Claim

### Prose Claim

A Status with a dedicated folder has one integer Status Order Number from 0 through 999. Order numbers are distinct across Status values. Declare each number once, including for a Status admitted by several Roles. Active uses its Container's base directory. AN-S-3160 specifies the YAML representation.

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
