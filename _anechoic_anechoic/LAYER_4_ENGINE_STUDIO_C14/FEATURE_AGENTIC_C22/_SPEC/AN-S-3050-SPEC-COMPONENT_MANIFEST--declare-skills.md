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
  status: active
  version: 3
  updated_at: "2026-11-24T23:12:55.813309+00:00"
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
        boundaries={'code': {'imports': {'only': []}},
                    'state': {'reads': [], 'writes': []}},
    ),
)
```

## Boundary scope

This definition covers the ane skill carrier. It provides instructions for a consumer; it performs no MCP calls or state effects.
