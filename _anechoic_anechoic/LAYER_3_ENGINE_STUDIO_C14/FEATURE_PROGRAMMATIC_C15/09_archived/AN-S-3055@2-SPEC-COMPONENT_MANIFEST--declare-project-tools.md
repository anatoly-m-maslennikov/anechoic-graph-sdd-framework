---
atom_family: SPEC
atom_id: AN-S-3055
container:
  component: C15
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 2
  updated_at: '2026-11-21T18:47:45.603340+00:00'
---

## Summary

Declare PROJECT_TOOLS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C19',
        name='PROJECT_TOOLS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code_access': {
                'exports': {
                    'test_suite__pub': 'public',
                    'test_suite__pub.run_full_suite': 'public',
                },
            },
        },
    ),
)
```
