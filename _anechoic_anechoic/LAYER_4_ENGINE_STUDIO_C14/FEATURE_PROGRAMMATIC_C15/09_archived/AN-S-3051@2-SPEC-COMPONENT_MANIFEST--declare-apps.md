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
  status: archived
  version: 2
  updated_at: '2026-11-22T11:23:40.206159+00:00'
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
        boundaries={'code': {'imports': [], 'exports': {}}},
    ),
)
```

## Details

C20 is a grouping placeholder. Its current App directories contain no executable entry point; it declares no code, IO, or state boundary.
