---
atom_family: SPEC
atom_id: AN-S-3046
container:
  component: C14
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 4
  updated_at: "2026-11-24T23:12:55.813309+00:00"
relations:
  CONTRIBUTES_TO:
  - AN-S-3330
---

## Summary

Declare WORKBENCH

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C43',
        name='WORKBENCH',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {'imports': []},
            'io': {'client': {'workbench': {'component': 'C21', 'interface': 'workbench_http'}}},
            'state': {'reads': [], 'writes': []},
        },
    ),
)
```
