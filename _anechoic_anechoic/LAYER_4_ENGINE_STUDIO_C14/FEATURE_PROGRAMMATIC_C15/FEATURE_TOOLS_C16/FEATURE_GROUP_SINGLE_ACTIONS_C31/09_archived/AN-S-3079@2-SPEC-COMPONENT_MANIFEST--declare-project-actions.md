---
atom_family: SPEC
atom_id: AN-S-3079
container:
  component: C31
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:01.048282+00:00"
---

## Summary

Declare PROJECT_ACTIONS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C39',
        name='PROJECT_ACTIONS',
        lens_whitelist=[],
    ),
)
```
