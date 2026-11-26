---
atom_family: SPEC
atom_id: AN-S-3042
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-25T11:13:52.932334+00:00"
---

## Summary

Declare Meta-methodology

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C58',
        name='Meta-methodology',
        layer=2,
        lens_whitelist=['DOM/MTD'],
    ),
)
```
