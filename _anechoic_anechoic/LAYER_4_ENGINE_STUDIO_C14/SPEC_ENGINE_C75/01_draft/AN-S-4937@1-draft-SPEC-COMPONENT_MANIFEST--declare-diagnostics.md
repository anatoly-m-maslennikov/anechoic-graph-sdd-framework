---
atom_family: SPEC
atom_id: AN-S-4937
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

Declare Diagnostics

## Purpose

Format source-linked gaps and unresolved findings as diagnostics.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C90',
        layer=1,
        name='Diagnostics',
        lens_whitelist=['DES', 'SPEC'],
        boundaries={
            'io': {'server': {'finding': {'outcomes': {
                'reported': {'must_effect': [('C90.source_diagnostic', 'formed')]},
            }}}},
        },
    ),
)
```
