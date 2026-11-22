---
atom_family: SPEC
atom_id: AN-S-3082
container:
  component: C43
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 11
  updated_at: '2026-11-22T11:23:40.206159+00:00'
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
                    'import_graph__shared.ImportSite': {'shared': ['C59']},
                    'import_graph__shared.Source': {'shared': ['C59', 'LAYER_3_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests']},
                    'import_graph__shared.capture': {'shared': ['C59']},
                    'import_graph__shared.code_access_occurrences': {'shared': ['C59']},
                    'import_graph__shared.excluded_source_path': {'shared': ['C59']},
                    'import_graph__shared.event_path': {'shared': ['C59']},
                    'import_graph__shared.git_ignored': {'shared': ['C59']},
                    'import_graph__shared.iter_files': {'shared': ['C59']},
                    'import_graph__shared.relative_path': {'shared': ['C59']},
                    'import_graph__shared.relevant_change': {'shared': ['C59']},
                    'import_graph__shared.resolve_realization': {'shared': ['C59']},
                },
            },
            'io': {
                'client': [
                    {'transport': 'cli', 'command': ['git', '-C', '<project-root>', 'rev-parse', '--show-toplevel']},
                    {'transport': 'cli', 'command': ['git', '-C', '<worktree-root>', 'check-ignore', '--stdin', '-z']},
                ],
            },
            'state': {
                'reads': ['admitted Project source inventory', 'dependency manifests', 'installed Python distribution metadata'],
                'writes': [],
            },
        },
    ),
)
```
