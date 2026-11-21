---
atom_family: SPEC
atom_id: AN-S-3059
container:
  component: C43
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 3
  updated_at: '2026-11-21T22:51:12.819403+00:00'
---

## Summary

Declare WORKBENCH_BACKEND

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C45',
        name='WORKBENCH_BACKEND',
        lens_whitelist=['DES', 'DES/DOM', 'DevOps', 'QA', 'SPEC', 'SWD'],
        boundaries={
            'code': {
                'exports': {
                    'FEATURE_WORKBENCH_BACKEND__shared': None,
                    'FEATURE_WORKBENCH_BACKEND__shared.SourceReader': None,
                    'FEATURE_WORKBENCH_BACKEND__pub': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.ServiceInterface': 'public',
                },
            },
        },
    ),
)
```
