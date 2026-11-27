---
atom_family: SPEC
atom_id: AN-S-3071
container:
  component: C16
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 3
  updated_at: "2026-11-26T15:52:29.571720+00:00"
---

## Summary

Declare SINGLE_ACTIONS

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C31',
    name='SINGLE_ACTIONS',
    lens_whitelist=['DES', 'SPEC', 'SWD'],
)
```
