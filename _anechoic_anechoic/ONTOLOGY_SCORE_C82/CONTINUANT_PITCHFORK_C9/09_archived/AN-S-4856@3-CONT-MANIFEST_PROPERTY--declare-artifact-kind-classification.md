---
atom_family: SPEC
atom_id: AN-S-4856
concern:
  subject: Artifact Kind
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
  updated_at: "2026-11-26T18:34:34.838401+00:00"
---

## Summary

Declare Artifact Kind classification

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Classification, Property

class Property4856(Property):
    name = 'Artifact Kind'
    bearer = Classification
    property.classification = True
    property.value.allowed = ('Artifact', 'Ephemeral')
```
