---
atom_family: SPEC
atom_id: AN-S-4931
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

Declare Lean Translator

## Purpose

Take pinned declarations and translate the model normalized by C85
into Lean declarations.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C84',
        layer=3,
        name='Lean Translator',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'io': {'server': {'compile_lean': {'outcomes': {
                'compiled': {'must_effect': [('C84.lean_source', 'generated')]},
            }}}},
        },
    ),
)
```
