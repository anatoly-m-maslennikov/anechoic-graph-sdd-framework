---
atom_family: SPEC
atom_id: AN-S-3059
structure:
  container:
    component: C43
  tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-21T13:07:38.641882+00:00"
---

## Summary

Declare WORKBENCH_BACKEND

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C45',
        name='WORKBENCH_BACKEND',
        lens_whitelist=['DES', 'DES/DOM', 'DevOps', 'QA', 'SPEC', 'SWD'],
    ),
)
```
