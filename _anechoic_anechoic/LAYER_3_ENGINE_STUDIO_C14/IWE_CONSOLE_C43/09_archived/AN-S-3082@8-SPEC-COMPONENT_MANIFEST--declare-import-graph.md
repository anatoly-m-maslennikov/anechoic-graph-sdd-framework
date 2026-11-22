---
atom_family: SPEC
atom_id: AN-S-3082
container:
  component: C43
tier: 0
context:
  template: component_manifest
  lens: SPEC
state:
  status: "archived"
  version: 8
  updated_at: "2026-11-22T07:35:21.125216+00:00"
---

## Summary

Declare IMPORT_GRAPH

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C61',
        name='IMPORT_GRAPH',
        lens_whitelist=['DES', 'QA', 'SWD'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {
                    'source._parse': {'private': ['LAYER_3_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'import_graph__shared': None,
                    'import_graph__shared.ImportSite': None,
                    'import_graph__shared.Source': {'shared': ['LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests']},
                    'import_graph__shared.capture': None,
                    'import_graph__shared.code_access_occurrences': None,
                    'import_graph__shared.excluded_source_path': None,
                    'import_graph__shared.event_path': None,
                    'import_graph__shared.git_ignored': None,
                    'import_graph__shared.iter_files': None,
                    'import_graph__shared.relative_path': None,
                    'import_graph__shared.relevant_change': None,
                    'import_graph__shared.resolve_realization': None,
                },
            },
        },
    ),
)
```
