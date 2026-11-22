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
  status: "archived"
  version: 13
  updated_at: "2026-11-22T14:22:43.780786+00:00"
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
                'imports': {'only': ['ADAPTERS_C30__shared.parse_structure', 'ADAPTERS_C30__shared.realization_component_paths']},
                'exports': {
                    'import_graph__shared': None,
                    'import_graph__shared.ImportSite': {'shared': ['C59']},
                    'import_graph__shared.Source': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests']},
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
                'server': {'build_graph': {'transport': 'cli',
                                 'runner': 'managed_python',
                                 'module': 'IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.realization_graph_cli',
                                 'input_fields': ['root', 'config'],
                                 'optional_paired_inputs': ['structure', 'control_root'],
                                 'output_fields': ['nodes',
                                                   'occurrences',
                                                   'edges',
                                                   'test_edges',
                                                   'read_issues']}},
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
