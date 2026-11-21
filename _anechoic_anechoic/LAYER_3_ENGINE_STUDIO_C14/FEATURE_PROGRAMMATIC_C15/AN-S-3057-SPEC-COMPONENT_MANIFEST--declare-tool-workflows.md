---
atom_family: SPEC
atom_id: AN-S-3057
structure:
  container:
    component: C15
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

Declare TOOL_WORKFLOWS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C18',
        name='TOOL_WORKFLOWS',
        lens_whitelist=['DES', 'DES/DOM', 'DevOps', 'QA', 'SWD'],
    ),
)
```
