---
atom_family: SPEC
atom_id: AN-S-3039
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: '2026-11-22T12:00:09.602716+00:00'
---

## Summary

Declare Engine Studio

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C14',
        name='Engine Studio',
        layer=4,
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
    ),
)
```
