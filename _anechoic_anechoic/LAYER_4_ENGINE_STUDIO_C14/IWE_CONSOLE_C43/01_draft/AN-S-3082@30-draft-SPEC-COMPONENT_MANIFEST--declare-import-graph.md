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
  status: draft
  version: 30
  updated_at: "2026-11-24T23:12:55.813309+00:00"
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
            'code': {'exports': {'import_graph__shared': None,
                         'import_graph__shared.ImportSite': {'shared': ['C59',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                         'import_graph__shared.PACKAGE_SUFFIX': {'shared': ['C59']},
                         'import_graph__shared.SUFFIX': {'shared': ['C59']},
                         'import_graph__shared.Source': {'shared': ['C59',
                                                                    'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                         'import_graph__shared._read_pins': {'shared': ['C59',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests']},
                         'import_graph__shared.analyze_state': {'shared': ['C59']},
                         'import_graph__shared.capture': {'shared': ['C59',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                         'import_graph__shared.code_access_occurrences': {'shared': ['C59',
                                                                                     'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                         'import_graph__shared.compile_workflow': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                         'import_graph__shared.event_path': {'shared': ['C59']},
                         'import_graph__shared.excluded_source_path': {'shared': ['C59']},
                         'import_graph__shared.git_ignored': {'shared': ['C59',
                                                                         'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                         'import_graph__shared.graph_input_signature': {'shared': ['C69',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                         'import_graph__shared.is_trace_path': {'shared': ['C59',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                         'import_graph__shared.iter_files': {'shared': ['C59']},
                         'import_graph__shared.native_trace_rows': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                         'import_graph__shared.native_trace_snapshot': {'shared': ['C59']},
                         'import_graph__shared.relative_path': {'shared': ['C59']},
                         'import_graph__shared.relevant_change': {'shared': ['C59',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                         'import_graph__shared.resolve_realization': {'shared': ['C59',
                                                                                 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                         'import_graph__shared.run_graph_build': {'shared': ['C69',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                         'import_graph__shared.web_state_cases': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']}},
             'imports': {'only': ['ADAPTERS_C30__shared.UniqueSafeLoader',
                                  'ADAPTERS_C30__shared.check_yaml_resources',
                                  'ADAPTERS_C30__shared.formal_claim_fences',
                                  'ADAPTERS_C30__shared.parse_structure',
                                  'ADAPTERS_C30__shared.realization_component_paths',
                                  'FEATURE_MODEL_VALIDATION__shared.check_code_access',
                                  'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75.LAYER_2_FORMAL_SPECIFICATION_C94.LAYER_2_SPEC_READING_C83.SPECIFICATION_MODEL_C85._package__shared.parse_workflow',
                                  'FEATURE_PROGRAMMATIC.SPEC_ENGINE_C75._package__shared.compile_workflow',
                                  'import_graph__shared.capture',
                                  'import_graph__shared.code_access_occurrences',
                                  'import_graph__shared.compile_workflow',
                                  'import_graph__shared.git_ignored',
                                  'import_graph__shared.graph_input_signature',
                                  'import_graph__shared.relevant_change',
                                  'import_graph__shared.resolve_realization',
                                  'import_graph__shared.run_graph_build',
                                  'import_graph__shared.web_state_cases',
                                  'metrics__shared.is_measurement_input',
                                  'realization_ownership__pub.build_code_access_ownership']}},
            'io': {
                'server': {'build_graph': {'transport': 'cli',
                                 'runner': 'managed_python',
                                 'module': 'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.realization_graph_cli',
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
                                               'module': 'LAYER_4_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_ownership',
                                               'arguments': ['<project-root>']},
                           'workflow_spec': {'transport': 'cli', 'runner': 'managed_python',
                                 'module': 'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.workflow_spec',
                                 'arguments': ['<solution-atom>', 'render or check <trace>'],
                                 'output': 'Mermaid or a JSON flow check'},
                           'workflow_reuse': {'transport': 'cli', 'runner': 'managed_python',
                                 'module': 'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.workflow_reuse',
                                 'input_fields': ['root', 'control_root', 'graph', 'structure', 'caller', 'callee'],
                                 'optional_paired_inputs': ['first', 'last'],
                                 'output': 'JSON reuse finding'}},
                'client': [
                    {'transport': 'cli', 'optional': True,
                     'command': ['lean', '--run', 'WorkflowTrace.lean'],
                     'input': 'JSON workflow model and trace'},
                    {'transport': 'cli', 'optional': True,
                     'command': ['lean', '--run', 'FlowComparison.lean'],
                     'input': 'JSON pair of source-derived effect sequences'},
                    {'transport': 'cli', 'optional': True, 'command': ['lean', '--run', 'ActionEffects.lean'],
                     'input': 'JSON batch of ordered state cases on stdin'},
                    {'transport': 'cli', 'optional': True, 'command': ['node',
                     'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/scripts/import-graph-scanner.ts'],
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
