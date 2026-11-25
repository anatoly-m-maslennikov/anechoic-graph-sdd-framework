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
  status: draft
  version: 5
  updated_at: '2026-11-25T21:46:13.372267+00:00'
---

## Summary

Declare Meta-methodology

## Purpose

Meta-methodology declarations define how work is done.

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
        boundaries={'state': {'reads': [], 'writes': []},
         'io': {'server': {'provide_meta_methodology_sources': {'outcomes': {'declarations_available': {'must_effect': [('C58.meta_methodology',
                                                                                                                         'available')]}}}}}},
    ),
)
```
