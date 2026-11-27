---
atom_family: SPEC
atom_id: AN-S-3070
container:
  component: C16
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:00.998589+00:00"
---

## Summary

Declare SCHEDULERS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C32',
        name='SCHEDULERS',
        lens_whitelist=['DES', 'SPEC', 'SWD'],
    ),
)
```
