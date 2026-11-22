---
atom_family: SPEC
atom_id: AN-S-3078
container:
  component: C31
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T11:23:40.206159+00:00'
---

## Summary

Declare PROJECTION_ACTIONS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C37',
        name='PROJECTION_ACTIONS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
    ),
)
```
