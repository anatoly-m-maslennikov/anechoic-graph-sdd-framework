---
atom_family: SPEC
atom_id: AN-S-3069
container:
  component: C16
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T01:47:19.816295+00:00"
---

## Summary

Declare ADAPTERS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C30',
        name='ADAPTERS',
        lens_whitelist=['SWD'],
    ),
)
```
