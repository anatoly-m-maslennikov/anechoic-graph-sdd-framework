---
atom_family: SPEC
atom_id: AN-S-3063
container:
  component: C24
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-19T00:00:00Z'
---

## Summary

Declare SUBJECT_ATOM_GATHERER_PROMPT

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C57',
        name='SUBJECT_ATOM_GATHERER_PROMPT',
        lens_whitelist=['DES'],
    ),
)
```
