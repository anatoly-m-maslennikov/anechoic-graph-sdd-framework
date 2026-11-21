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
  status: "active"
  version: 2
  updated_at: "2026-11-21T14:26:34.288257+00:00"
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
        boundaries={
            'code_access': {
                'imports': ['C15', 'C16', 'C45', 'C62'],
            },
        },
    ),
)
```
