---
atom_family: SPEC
atom_id: AN-S-3048
container:
  component: C14
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:27.189732+00:00"
---

## Summary

Declare Backend Deck

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C60',
    name='Backend Deck',
    lens_whitelist=['SPEC'],
)
```
