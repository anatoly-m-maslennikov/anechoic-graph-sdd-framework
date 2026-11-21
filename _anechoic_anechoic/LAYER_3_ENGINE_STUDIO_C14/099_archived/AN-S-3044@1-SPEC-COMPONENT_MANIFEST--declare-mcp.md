---
atom_family: SPEC
atom_id: AN-S-3044
structure:
  container:
    component: C14
  tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-21T14:26:34.287367+00:00"
---

## Summary

Declare MCP

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C21',
        name='MCP',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
    ),
)
```
