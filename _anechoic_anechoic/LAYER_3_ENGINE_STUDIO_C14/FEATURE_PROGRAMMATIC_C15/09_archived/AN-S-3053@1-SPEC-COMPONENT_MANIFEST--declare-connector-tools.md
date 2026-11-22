---
atom_family: SPEC
atom_id: AN-S-3053
container:
  component: C15
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-19T00:00:00Z'
---

## Summary

Declare CONNECTOR_TOOLS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C17',
        name='CONNECTOR_TOOLS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
    ),
)
```
