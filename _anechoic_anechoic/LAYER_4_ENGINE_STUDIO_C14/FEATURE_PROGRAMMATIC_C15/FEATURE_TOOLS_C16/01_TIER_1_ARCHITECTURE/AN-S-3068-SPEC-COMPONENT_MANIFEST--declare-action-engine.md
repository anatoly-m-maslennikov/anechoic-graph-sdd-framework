---
atom_family: SPEC
atom_id: AN-S-3068
container:
  component: C16
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:29.370330+00:00"
---

## Summary

Declare ACTION_ENGINE

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C34',
    name='ACTION_ENGINE',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```
