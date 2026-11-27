---
atom_family: SPEC
atom_id: AN-S-3131
concern:
  subject: Lens Whitelist
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest
  relation: is_property_of
container:
  component: C9
tier: 2
context:
  template: manifest_property
  lens: DOM/CONT
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:32.448052+00:00"
---

## Summary

Declare Lens Whitelist

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Manifest, Property

class Property3131(Property):
    name = 'Lens Whitelist'
    bearer = Manifest
    field_options = {'default': None, 'kw_only': True}
    property.value.format = list[str] | None
```
