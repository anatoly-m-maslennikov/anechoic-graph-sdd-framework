---
atom_family: SPEC
atom_id: AN-S-4856
concern:
  subject: Persistence
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

Declare the Persistence Axis

## Semantics

An Artifact has a retained Carrier. An Ephemeral entity exists for an operating context such as a session.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Node, Property

class Property4856(Property):
    name = 'Persistence'
    bearer = Node
    property.axis = True
    property.value.allowed = ('Artifact', 'Ephemeral')
```
