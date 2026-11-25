---
atom_family: SPEC
atom_id: AN-S-3042
container:
  component: C82
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 4
  updated_at: '2026-11-25T13:32:29.996231+00:00'
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
        name='Occurrent Metronome',
        layer=2,
        lens_whitelist=['DOM/MTD'],
    ),
)
```
