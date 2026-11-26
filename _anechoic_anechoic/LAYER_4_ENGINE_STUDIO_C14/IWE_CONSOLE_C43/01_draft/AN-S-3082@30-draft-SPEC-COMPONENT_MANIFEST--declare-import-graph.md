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
            'code': {
                'imports': {'only': ['metrics__shared.is_measurement_input',
                                     'ADAPTERS_C30__shared.UniqueSafeLoader', 'ADAPTERS_C30__shared.check_yaml_resources',
                                     'ADAPTERS_C30__shared.parse_structure', 'ADAPTERS_C30__shared.realization_component_paths',
                                     'ADAPTERS_C30__shared.formal_claim_fences',
                                     'realization_ownership__pub.build_code_access_ownership',
                                     'FEATURE_MODEL_VALIDATION__shared.check_code_access']},
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
                                 'output': 'Mermaid or a JSON flow check'},
                           'workflow_reuse': {'transport': 'cli', 'runner': 'managed_python',
                                 'module': 'IWE_CONSOLE_C43.APP_WORKBENCH.FEATURE_IMPORT_GRAPH_C61.workflow_reuse',
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
