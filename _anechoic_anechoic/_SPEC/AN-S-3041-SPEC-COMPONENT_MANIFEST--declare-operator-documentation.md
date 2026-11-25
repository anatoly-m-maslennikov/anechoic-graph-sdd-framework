---
atom_family: SPEC
atom_id: AN-S-3041
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: '2026-11-24T14:38:16.546723+00:00'
---

## Summary

Declare Operator Documentation

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C25',
        name='Operator Documentation',
        layer=6,
        lens_whitelist=['DevOps'],
    ),
)
```
