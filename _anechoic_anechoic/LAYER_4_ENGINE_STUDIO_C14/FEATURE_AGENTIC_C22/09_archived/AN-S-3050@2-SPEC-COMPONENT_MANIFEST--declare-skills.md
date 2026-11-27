---
atom_family: SPEC
atom_id: AN-S-3050
container:
  component: C22
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-26T15:54:01.177740+00:00"
---

## Summary

Declare SKILLS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C23',
        name='SKILLS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={'code': {'imports': {'only': []}, 'exports': {}},
                    'state': {'reads': [], 'writes': []}},
    ),
)
```

## Boundary scope

This definition covers the ane skill carrier. It provides instructions for a consumer; it performs no MCP calls or state effects.
