---
atom_family: SPEC
atom_id: AN-S-3400
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-23T09:15:54.889519+00:00'
---

## Summary

Declare Assets

## Purpose

Maintain the source files for Anechoic brand assets.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C78',
        name='Assets',
        lens_whitelist=['DES', 'SPEC'],
    ),
)
```
