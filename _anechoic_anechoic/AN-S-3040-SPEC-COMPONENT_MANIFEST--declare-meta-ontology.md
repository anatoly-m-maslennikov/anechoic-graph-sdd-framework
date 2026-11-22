---
atom_family: SPEC
atom_id: AN-S-3040
container:
  component: C00
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: '2026-11-22T11:23:40.206159+00:00'
relations:
  CONTRIBUTES_TO:
  - AN-S-3328
---

## Summary

Declare Meta-ontology

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C9',
        name='Meta-ontology',
        layer=1,
        lens_whitelist=['DES', 'DES/DOM', 'DevOps', 'QA', 'SWD'],
    ),
)
```
