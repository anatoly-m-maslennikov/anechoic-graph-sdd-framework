---
atom_family: SPEC
atom_id: AN-S-4858
concern:
  subject: Authority
  path: Model/Graph/Classification
  relation: classifies
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-26T18:34:34.847697+00:00"
---

## Summary

Declare Authority classification

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Classification, Property

class Property4858(Property):
    name = 'Authority'
    bearer = Classification
    property.classification = True
    property.value.allowed = ('SSOT', 'Derived')
```
