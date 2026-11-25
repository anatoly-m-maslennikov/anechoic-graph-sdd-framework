---
atom_family: SPEC
atom_id: AN-S-3060
container:
  component: C43
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: archived
  version: 8
  updated_at: '2026-11-24T19:35:54.327066+00:00'
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
                'imports': {'only': ['src.lib.lib__shared']},
                'exports': {
                    'FEATURE_WORKBENCH_FRONTEND__shared': None,
                    'src.lib.lib__shared': {'shared': ['C46', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/src',
                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/FEATURE_WORKBENCH_FRONTEND__tests']},
                    'FEATURE_WORKBENCH_FRONTEND__shared.WorkbenchApi': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.WorkspaceApi': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.HttpOperationCaller': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.McpAppTransport': None,
                    'FEATURE_WORKBENCH_FRONTEND__shared.OperationCaller': None,
                },
            },
            'io': {
                'server': {
                    'source_imports': {'transport': 'cli', 'runner': 'node',
                                       'path': 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/scripts/import-graph-scanner.mjs'},
                    'source_function_sizes': {
                        'transport': 'cli',
                        'runner': 'node',
                        'path': 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/scripts/source-function-sizes.ts',
                    },
                },
                'client': [{'component': 'C21', 'interface': 'workbench_http'}],
            },
            'state': {
                'reads': ['selected Project Workspace and View', 'query pages and check verdicts'],
                'writes': ['browser preferences', 'editor and View display state', 'standalone browser drafts'],
            },
        },
    ),
)
```
