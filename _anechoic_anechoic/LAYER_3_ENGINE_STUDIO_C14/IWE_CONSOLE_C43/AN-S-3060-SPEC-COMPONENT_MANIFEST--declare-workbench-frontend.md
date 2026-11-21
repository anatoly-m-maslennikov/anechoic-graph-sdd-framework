---
atom_family: SPEC
atom_id: AN-S-3060
structure:
  container:
    component: C43
  tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 2
  updated_at: "2026-11-21T12:30:01.390349+00:00"
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
            'code_access': {
                'imports': [],
                'exports': {
                    'FEATURE_WORKBENCH_FRONTEND__family_pub': None,
                    'FEATURE_WORKBENCH_FRONTEND__family_pub.WorkbenchApi': None,
                    'FEATURE_WORKBENCH_FRONTEND__family_pub.WorkspaceApi': None,
                    'FEATURE_WORKBENCH_FRONTEND__family_pub.HttpOperationCaller': None,
                    'FEATURE_WORKBENCH_FRONTEND__family_pub.McpAppTransport': None,
                    'FEATURE_WORKBENCH_FRONTEND__family_pub.OperationCaller': None,
                },
            },
        },
    ),
)
```
