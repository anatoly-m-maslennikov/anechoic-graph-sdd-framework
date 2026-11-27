---
atom_family: SPEC
atom_id: AN-S-4909
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-26T15:54:00.652087+00:00"
---

## Summary

Declare Ontology Score

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C82',
        name='Ontology Score',
        lens_whitelist=['SPEC'],
    ),
)
```
