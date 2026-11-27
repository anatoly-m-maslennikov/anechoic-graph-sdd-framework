---
atom_family: SPEC
atom_id: AN-S-3070
container:
  component: C16
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 3
  updated_at: "2026-11-26T15:52:29.516351+00:00"
---

## Summary

Declare SCHEDULERS

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C32',
    name='SCHEDULERS',
    lens_whitelist=['DES', 'SPEC', 'SWD'],
)
```
