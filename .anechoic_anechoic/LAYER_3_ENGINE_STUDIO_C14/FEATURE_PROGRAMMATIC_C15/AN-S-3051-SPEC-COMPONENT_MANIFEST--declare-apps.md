---
atom_family: SPEC
atom_id: AN-S-3051
structure:
  container:
    component: C15
  tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-19T00:00:00Z'
---

## Summary

Declare APPS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C20',
        name='APPS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
    ),
)
```
