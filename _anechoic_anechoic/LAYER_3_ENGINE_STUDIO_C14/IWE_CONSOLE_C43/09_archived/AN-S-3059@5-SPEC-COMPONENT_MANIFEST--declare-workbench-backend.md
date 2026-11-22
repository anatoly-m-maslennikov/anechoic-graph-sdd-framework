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
  status: "archived"
  version: 5
  updated_at: "2026-11-22T00:32:19.974473+00:00"
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
                'imports': ['C53'],
                'exports': {
                    'FEATURE_WORKBENCH_BACKEND__shared': None,
                    'FEATURE_WORKBENCH_BACKEND__shared.SourceReader': None,
                    'FEATURE_WORKBENCH_BACKEND__shared.boundary_tables': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP']},
                    'FEATURE_WORKBENCH_BACKEND__pub': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.ServiceInterface': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.DELIVERY_MODES': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.QueryExecutionError': 'public',
                    'FEATURE_WORKBENCH_BACKEND__pub.WorkbenchUnavailableError': 'public',
                },
            },
        },
    ),
)
```
