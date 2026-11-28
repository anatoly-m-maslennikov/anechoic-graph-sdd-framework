---
atom_family: SPEC
atom_id: AN-S-4858
concern:
  subject: Authority
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
  version: 5
  updated_at: "2026-11-28T10:28:09.160093+00:00"
---

## Summary

Declare the Authority Axis

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node, Property

class Property4858(Property):
    name = 'Authority'
    bearer = Node
    property.axis = True
    property.value.allowed = ('SSOT', 'Derived')
```
