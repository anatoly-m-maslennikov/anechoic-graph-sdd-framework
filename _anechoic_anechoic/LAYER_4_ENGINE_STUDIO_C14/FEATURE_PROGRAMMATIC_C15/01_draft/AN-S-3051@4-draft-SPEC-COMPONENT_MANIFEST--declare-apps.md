---
atom_family: SPEC
atom_id: AN-S-3051
container:
  component: C15
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T11:11:23.887958+00:00'
---

## Summary

Declare APPS

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C20',
        name='APPS',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={'code': {'imports': []}, 'io': {'server': {}}},
    ),
)
```

## Details

C20 is a grouping placeholder. Its current App directories contain no
executable entry point. The grouping has no direct server interface.
