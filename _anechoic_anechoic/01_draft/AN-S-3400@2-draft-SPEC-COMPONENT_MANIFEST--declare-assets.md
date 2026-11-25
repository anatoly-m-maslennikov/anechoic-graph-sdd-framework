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
  status: draft
  version: 2
  updated_at: '2026-11-26T00:00:00Z'
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
        boundaries={'io': {'server': {'describe_assets_scope': {'outcomes': {'assets_scope_described': {
            'must_effect': [('assets.logo', 'declared')],
        }}}}}},
    ),
)
```

## Boundary scope

This describes the source resource boundary. It does not assert a callable operation or a runtime effect.
