---
atom_family: SPEC
atom_id: AN-S-3071
container:
  component: C16
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

Declare SINGLE_ACTIONS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C31',
        name='SINGLE_ACTIONS',
        lens_whitelist=['DES', 'SPEC', 'SWD'],
    ),
)
```
