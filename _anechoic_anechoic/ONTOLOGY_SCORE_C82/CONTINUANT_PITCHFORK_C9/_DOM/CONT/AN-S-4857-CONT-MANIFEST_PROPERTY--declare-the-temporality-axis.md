---
atom_family: SPEC
atom_id: AN-S-4857
concern:
  subject: Temporality
  path: Model/Graph/Node
  relation: has_axis
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: active
  version: 6
  updated_at: "2026-11-28T10:28:09.160093+00:00"
---

## Summary

Declare the Temporality Axis

## Semantics

A Continuant endures through time. An Occurrent unfolds through time.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node, Property

class Property4857(Property):
    name = 'Temporality'
    bearer = Node
    property.axis = True
    property.value.allowed = ('Continuant', 'Occurrent')
```
