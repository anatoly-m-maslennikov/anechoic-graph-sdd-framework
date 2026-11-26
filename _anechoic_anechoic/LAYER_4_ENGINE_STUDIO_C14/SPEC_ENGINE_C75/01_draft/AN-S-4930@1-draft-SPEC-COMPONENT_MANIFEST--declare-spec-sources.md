---
atom_family: SPEC
atom_id: AN-S-4930
container:
  component: C75
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T20:39:08.202192+00:00'
---
## Summary

Declare Spec Sources

## Purpose

Load pinned Spec sources and validate their declarations and links.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C83',
        layer=1,
        name='Spec Sources',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'code': {'imports': ['C30']},
            'io': {'server': {'load_boundary_model': {'outcomes': {
                'loaded': {'must_effect': [('C83.pinned_sources', 'loaded')]},
            }}}},
        },
    ),
)
```
