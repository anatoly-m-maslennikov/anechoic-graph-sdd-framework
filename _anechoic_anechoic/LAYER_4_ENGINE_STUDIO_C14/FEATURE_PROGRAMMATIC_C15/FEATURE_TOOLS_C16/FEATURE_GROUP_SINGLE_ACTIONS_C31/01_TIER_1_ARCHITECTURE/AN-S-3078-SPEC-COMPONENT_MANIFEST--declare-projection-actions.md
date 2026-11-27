---
atom_family: SPEC
atom_id: AN-S-3078
container:
  component: C31
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:29.686903+00:00"
---

## Summary

Declare PROJECTION_ACTIONS

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C37',
    name='PROJECTION_ACTIONS',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```
