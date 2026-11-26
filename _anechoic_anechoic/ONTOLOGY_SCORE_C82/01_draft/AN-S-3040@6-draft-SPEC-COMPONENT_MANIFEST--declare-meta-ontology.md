---
atom_family: SPEC
atom_id: AN-S-3040
container:
  component: C82
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 6
  updated_at: '2026-11-25T21:46:13.372267+00:00'
relations:
  CONTRIBUTES_TO:
  - AN-S-3328
---

## Summary

Declare Meta-ontology

## Purpose

Meta-ontology declarations define the Project model vocabulary.

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C9',
        name='Continuant Pitchfork',
        layer=1,
        lens_whitelist=['DES', 'DES/DOM', 'DOM/ONT', 'DevOps', 'QA', 'SWD'],
        boundaries={'state': {'reads': [], 'writes': []},
         'io': {'server': {'provide_meta_ontology_sources': {'outcomes': {'declarations_available': {'must_effect': [('C9.meta_ontology',
                                                                                                                      'available')]}}}}}},
    ),
)
```
