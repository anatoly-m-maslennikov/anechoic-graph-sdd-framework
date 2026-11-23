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
  status: archived
  version: 25
  updated_at: '2026-11-23T04:32:26.395669+00:00'
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
                'imports': {'only': ['metrics__shared.is_measurement_input',
                                     'ADAPTERS_C30__shared.UniqueSafeLoader', 'ADAPTERS_C30__shared.check_yaml_resources',
                                     'ADAPTERS_C30__shared.parse_structure', 'ADAPTERS_C30__shared.realization_component_paths',
                                     'ADAPTERS_C30__shared.formal_claim_fences',
                                     'realization_ownership__pub.build_code_access_ownership',
                                     'FEATURE_MODEL_VALIDATION__shared.check_code_access']},
                'exports': {
                    'import_graph__shared': None,
                    'trace_bindings__shared.PACKAGE_SUFFIX': {'shared': ['C59']},
                    'trace_bindings__shared.SUFFIX': {'shared': ['C59']},
                    'trace_bindings__shared._read_pins': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                    'trace_bindings__shared.is_trace_path': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests']},
                    'trace_bindings__shared.native_trace_rows': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests']},
                    'trace_bindings__shared.native_trace_snapshot': {'shared': ['C59']},
                    'import_graph__shared.analyze_state': {'shared': ['C59']},
                    'import_graph__shared.run_graph_build': {'shared': ['C69']},
                    'import_graph__shared.graph_input_signature': {'shared': ['C69', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                    'import_graph__shared.ImportSite': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests']},
                    'import_graph__shared.Source': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/FEATURE_WORKBENCH_BACKEND__tests']},
                    'import_graph__shared.capture': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                    'import_graph__shared.code_access_occurrences': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                    'import_graph__shared.excluded_source_path': {'shared': ['C59']},
                    'import_graph__shared.event_path': {'shared': ['C59']},
                    'import_graph__shared.git_ignored': {'shared': ['C59']},
                    'import_graph__shared.iter_files': {'shared': ['C59']},
                    'import_graph__shared.relative_path': {'shared': ['C59']},
                    'import_graph__shared.relevant_change': {'shared': ['C59']},
                    'import_graph__shared.resolve_realization': {'shared': ['C59', 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
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
                                                   'read_issues',
                                                   'state_effect_findings',
                                                   'code_access_findings']},
                           'import_ownership': {'transport': 'cli', 'runner': 'managed_python',
                                               'module': 'LAYER_4_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.import_ownership',
                                               'arguments': ['<project-root>']},
                           'workflow_spec': {'transport': 'cli', 'runner': 'managed_python',
                                 'module': 'IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.workflow_spec',
                                 'arguments': ['<solution-atom>', 'render or check <trace>'],
                                 'output': 'Mermaid or a JSON flow check'}},
                'client': [
                    {'transport': 'cli', 'optional': True,
                     'command': ['lean', '--run', 'WorkflowTrace.lean'],
                     'input': 'JSON workflow model and trace'},
                    {'transport': 'cli', 'optional': True, 'command': ['lean', '--run', 'ActionEffects.lean'],
                     'input': 'JSON batch of ordered state cases on stdin'},
                    {'transport': 'cli', 'optional': True, 'command': ['node',
                     'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_WORKBENCH/FEATURE_WORKBENCH_FRONTEND/scripts/import-graph-scanner.mjs'],
                     'input': 'JSON source batch on stdin'},
                ],
            },
            'state': {
                'reads': ['admitted Project source inventory', 'dependency manifests', 'Git ignore metadata', 'installed Python distribution metadata'],
                'writes': [],
            },
        },
    ),
)
```
