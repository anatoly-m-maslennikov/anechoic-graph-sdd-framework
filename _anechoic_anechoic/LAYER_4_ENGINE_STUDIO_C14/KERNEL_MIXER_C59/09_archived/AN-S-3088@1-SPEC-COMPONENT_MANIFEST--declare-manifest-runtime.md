---
atom_family: SPEC
atom_id: AN-S-3088
container:
  component: C59
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T01:03:17.333297+00:00"
---

## Summary

Declare Manifest Runtime

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C62',
        name='Manifest Runtime',
        lens_whitelist=['SPEC'],
    ),
)
```
