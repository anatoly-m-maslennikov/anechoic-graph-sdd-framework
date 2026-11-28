---
atom_family: SPEC
atom_id: AN-S-4857
concern:
  subject: Temporality
  path: Model/Graph/Axis
  relation: has_axis
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: archived
  version: 5
  updated_at: '2026-11-26T18:38:58.296902+00:00'
---

## Summary

Declare the Temporality Axis

## Semantics

A Continuant endures through time. An Occurrent unfolds through time.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Axis, Property

class Property4857(Property):
    name = 'Temporality'
    bearer = Axis
    property.axis = True
    property.value.allowed = ('Continuant', 'Occurrent')
```
