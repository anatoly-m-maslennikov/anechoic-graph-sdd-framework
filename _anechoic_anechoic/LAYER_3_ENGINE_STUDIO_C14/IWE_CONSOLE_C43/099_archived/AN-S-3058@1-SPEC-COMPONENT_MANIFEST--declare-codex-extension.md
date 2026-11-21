---
atom_family: SPEC
atom_id: AN-S-3058
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
  updated_at: "2026-11-21T12:26:54.943432+00:00"
---

## Summary

Declare CODEX_EXTENSION

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C48',
        name='CODEX_EXTENSION',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
    ),
)
```
