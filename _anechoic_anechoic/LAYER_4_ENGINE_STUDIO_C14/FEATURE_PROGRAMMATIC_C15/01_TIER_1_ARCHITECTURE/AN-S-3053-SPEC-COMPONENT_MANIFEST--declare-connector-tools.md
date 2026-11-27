---
atom_family: SPEC
atom_id: AN-S-3053
container:
  component: C15
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:28.891046+00:00"
---

## Summary

Declare CONNECTOR_TOOLS

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C17',
    name='CONNECTOR_TOOLS',
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```
