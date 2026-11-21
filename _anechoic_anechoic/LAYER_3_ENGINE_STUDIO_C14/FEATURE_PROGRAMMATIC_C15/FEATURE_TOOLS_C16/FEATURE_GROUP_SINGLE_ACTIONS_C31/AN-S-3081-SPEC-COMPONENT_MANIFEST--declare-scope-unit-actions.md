---
atom_family: SPEC
atom_id: AN-S-3081
structure:
  container:
    component: C31
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

Declare SCOPE_UNIT_ACTIONS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C36',
        name='SCOPE_UNIT_ACTIONS',
        lens_whitelist=[],
    ),
)
```
