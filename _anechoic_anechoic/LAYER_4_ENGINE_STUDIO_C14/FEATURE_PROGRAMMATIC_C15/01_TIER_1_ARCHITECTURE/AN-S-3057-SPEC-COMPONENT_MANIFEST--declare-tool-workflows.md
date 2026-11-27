---
atom_family: SPEC
atom_id: AN-S-3057
container:
  component: C15
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 4
  updated_at: "2026-11-26T15:52:29.336154+00:00"
---

## Summary

Declare TOOL_WORKFLOWS

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C18',
    name='TOOL_WORKFLOWS',
    lens_whitelist=['DES', 'DES/DOM', 'DevOps', 'QA', 'SWD'],
)
```
