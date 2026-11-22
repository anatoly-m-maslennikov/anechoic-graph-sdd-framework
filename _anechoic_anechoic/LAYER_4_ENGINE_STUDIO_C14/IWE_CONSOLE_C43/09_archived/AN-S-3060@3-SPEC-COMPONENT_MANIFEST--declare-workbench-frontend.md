---
atom_family: SPEC
atom_id: AN-S-3060
container:
  component: C43
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 3
  updated_at: "2026-11-22T05:05:33.953382+00:00"
---

## Summary

Declare WORKBENCH_FRONTEND

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C46',
        name='WORKBENCH_FRONTEND',
        lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {
                    'FEATURE_WORKBENCH_FRONTEND__shared': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.WorkbenchApi': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.WorkspaceApi': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.HttpOperationCaller': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.McpAppTransport': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.OperationCaller': None,
                },
            },
        },
    ),
)
```
