---
atom_family: SPEC
atom_id: AN-S-3161
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.442096+00:00"
---

## Summary

Declare Header

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Atom, Property

class Property3161(Property):
    name = 'Header'
    bearer = Atom
    property.dependent_property.name.allowed = ('Atom Family', 'Atom ID', 'Concern', 'Container', 'Tier', 'Priority', 'Context', 'Relations', 'State')
    property.dependent_property.ordered_pairs = (('Atom Family', 'Atom ID'), ('Atom ID', 'Concern'), ('Concern', 'Container'), ('Container', 'Tier'), ('Tier', 'Priority'), ('Priority', 'Context'), ('Context', 'Relations'), ('Relations', 'State'))
    property.cardinality = 1
    property.value.cardinality = 0
    property.value.format = object
```
