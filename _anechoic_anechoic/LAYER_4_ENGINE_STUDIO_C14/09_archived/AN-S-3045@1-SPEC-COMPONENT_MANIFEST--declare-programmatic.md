---
atom_family: SPEC
atom_id: AN-S-3045
container:
  component: C14
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T01:43:51.486587+00:00"
---

## Summary

Declare PROGRAMMATIC

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C15',
        name='PROGRAMMATIC',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
    ),
)
```
