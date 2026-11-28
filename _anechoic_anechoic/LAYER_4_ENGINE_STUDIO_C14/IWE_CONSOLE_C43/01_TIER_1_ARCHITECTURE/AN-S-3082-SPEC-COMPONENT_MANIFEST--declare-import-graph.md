---
atom_family: SPEC
atom_id: AN-S-3082
container:
  component: C43
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 32
  updated_at: "2026-11-28T12:43:17+00:00"
---
## Summary

Declare IMPORT_GRAPH

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C61',
    name='IMPORT_GRAPH',
    lens_whitelist=['DES', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['metrics__shared.is_measurement_input',
                               'ADAPTERS_C30__shared.UniqueSafeLoader',
                               'ADAPTERS_C30__shared.check_yaml_resources',
                               'ADAPTERS_C30__shared.parse_structure',
                               'ADAPTERS_C30__shared.realization_component_paths',
                               'ADAPTERS_C30__shared.formal_claim_fences',
                               '_package__shared.compile_workflow',
                               '_package__shared.parse_workflow',
                               'structure__shared.build_code_access_ownership',
                               'FEATURE_MODEL_VALIDATION__shared.check_code_access',
                               'import_graph__shared.capture',
                               'import_graph__shared.code_access_occurrences',
                               'import_graph__shared.compile_workflow',
                               'import_graph__shared.git_ignored',
                               'import_graph__shared.graph_input_signature',
                               'import_graph__shared.relevant_change',
                               'import_graph__shared.resolve_realization',
                               'import_graph__shared.run_graph_build',
                               'import_graph__shared.web_state_cases',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.ImportSite',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.Source',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.capture',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.relevant_change',
                               'RESOLUTION.code_access_occurrences.code_access_occurrences',
                               'RESOLUTION.graph_inputs.graph_input_signature',
                               'RESOLUTION.RESOLUTION__shared.resolve_realization',
                               'STATE_ANALYSIS.STATE_ANALYSIS__shared.analyze_state',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.excluded_source_path',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._event_path',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._git_ignored',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._iter_files',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._relative',
                               'SOURCE_CAPTURE.source_language._file_language',
                               'STATE_ANALYSIS.WEB_STATE.WEB_STATE__shared.web_state_cases',
                               'SOURCE_CAPTURE.web_imports._WEB',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._root_path',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._stat_signature',
                               'STATE_ANALYSIS.STATE_ANALYSIS__shared._policy',
                               'WORKFLOW_FACTS.WORKFLOW_FACTS__shared.UnsupportedReuse',
                               'WORKFLOW_FACTS.WORKFLOW_FACTS__shared.find_reuse_region',
                               'WORKFLOW_FACTS.WORKFLOW_FACTS__shared.lower_reuse',
                               'RESOLUTION.analysis_inputs.analysis_inputs',
                               'RESOLUTION.graph_inputs._git_selection_witness',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._RESOLUTION_INPUTS',
                               'STATE_ANALYSIS.STATE_ANALYSIS__shared._SourceVersionChanged',
                               'STATE_ANALYSIS.STATE_ANALYSIS__shared._read',
                               'SOURCE_CAPTURE.web_imports.lookup_web',
                               'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._discover',
                               'STATE_ANALYSIS.STATE_ANALYSIS__shared._CHECKER',
                               'STATE_ANALYSIS.STATE_ANALYSIS__shared._LANGUAGES',
                               'SOURCE_CAPTURE.web_imports._FRONTEND',
                               'SOURCE_CAPTURE.web_imports._SCANNER',
                               'SOURCE_CAPTURE.web_imports.scan_web',
                               'STATE_ANALYSIS.WEB_STATE.WEB_STATE__shared._SCANNER',
                               'trace_bindings.native_trace_snapshot',
                               'realization_graph_cli._options',
                               'FEATURE_IMPORT_GRAPH_C61__tests.FEATURE_IMPORT_GRAPH_C61__tests__shared.run_provider',
                               'structure.realization_ownership__pub.build_code_access_ownership',
                               'structure.structure__shared.parse_structure',
                               'structure.structure__shared.realization_component_paths',
                               'carriers.content.content__shared.UniqueSafeLoader',
                               'carriers.content.content__shared.check_yaml_resources',
                               'access._package__shared.check_code_access',
                               'carriers.content.content__shared.formal_claim_fences']},
          'exports': {'import_graph__shared': None,
                      'import_graph__shared.file_language': {'shared': ['C19']},
                      'import_graph__shared.compile_workflow': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'import_graph__shared.web_state_cases': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'import_graph__shared.PACKAGE_SUFFIX': {'shared': ['C59',
                                                                         'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_runtime',
                                                                         'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit']},
                      'import_graph__shared.SUFFIX': {'shared': ['C59',
                                                                 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_runtime',
                                                                 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit']},
                      'import_graph__shared._read_pins': {'shared': ['C59',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/FEATURE_MCP__tests/integration/graph/group_1']},
                      'import_graph__shared.is_trace_path': {'shared': ['C59',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_runtime',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests/projection/trace']},
                      'import_graph__shared.native_trace_rows': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests',
                                                                            'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests/projection/trace']},
                      'import_graph__shared.native_trace_snapshot': {'shared': ['C59',
                                                                                'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_runtime',
                                                                                'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit']},
                      'import_graph__shared.analyze_state': {'shared': ['C59']},
                      'import_graph__shared.run_graph_build': {'shared': ['C69',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests/realization']},
                      'import_graph__shared.graph_input_signature': {'shared': ['C69',
                                                                                'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'import_graph__shared.ImportSite': {'shared': ['C59',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'import_graph__shared.Source': {'shared': ['C59',
                                                                 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests']},
                      'import_graph__shared.capture': {'shared': ['C59',
                                                                  'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'import_graph__shared.code_access_occurrences': {'shared': ['C59',
                                                                                  'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'import_graph__shared.excluded_source_path': {'shared': ['C59']},
                      'import_graph__shared.event_path': {'shared': ['C59']},
                      'import_graph__shared.git_ignored': {'shared': ['C59',
                                                                      'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'import_graph__shared.iter_files': {'shared': ['C59']},
                      'import_graph__shared.relative_path': {'shared': ['C59']},
                      'import_graph__shared.relevant_change': {'shared': ['C59',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'import_graph__shared.resolve_realization': {'shared': ['C59',
                                                                              'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.ImportSite': {'private': ['parent',
                                                                                       'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION',
                                                                                       'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/native_projection',
                                                                                       'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests/projection/imports']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.Source': {'private': ['parent',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/native_projection',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests/projection/imports',
                                                                                   'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_BACKEND/FEATURE_IWE_CONSOLE_BACKEND__tests/projection/trace']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.capture': {'private': ['parent',
                                                                                    'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit',
                                                                                    'C59',
                                                                                    'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests',
                                                                                    'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests/realization']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.relevant_change': {'private': ['parent',
                                                                                            'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit',
                                                                                            'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests/realization']},
                      'RESOLUTION.code_access_occurrences.code_access_occurrences': {'private': ['parent',
                                                                                                 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_query/query_database',
                                                                                                 'C59',
                                                                                                 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'RESOLUTION.graph_inputs.graph_input_signature': {'private': ['parent',
                                                                                    'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests/realization',
                                                                                    'LAYER_4_ENGINE_STUDIO_C14/WORKERS_beta_C69/refresh']},
                      'RESOLUTION.RESOLUTION__shared.resolve_realization': {'private': ['parent',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests/realization']},
                      'STATE_ANALYSIS.STATE_ANALYSIS__shared.analyze_state': {'private': ['parent',
                                                                                          'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_query/query_database',
                                                                                          'C59']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared.excluded_source_path': {'private': ['parent',
                                                                                                 'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._event_path': {'private': ['parent',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._git_ignored': {'private': ['parent',
                                                                                         'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION',
                                                                                         'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services',
                                                                                         'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._iter_files': {'private': ['parent',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION',
                                                                                        'LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._relative': {'private': ['parent']},
                      'SOURCE_CAPTURE.source_language._file_language': {'shared': ['C19']},
                      'STATE_ANALYSIS.WEB_STATE.WEB_STATE__shared.web_state_cases': {'private': ['C61',
                                                                                                 'parent',
                                                                                                 'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests/state']},
                      'SOURCE_CAPTURE.web_imports._WEB': {'private': ['parent',
                                                                      'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._root_path': {'private': ['parent',
                                                                                       'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._stat_signature': {'private': ['parent',
                                                                                            'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/STATE_ANALYSIS',
                                                                                            'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'STATE_ANALYSIS.STATE_ANALYSIS__shared._policy': {'private': ['parent']},
                      'WORKFLOW_FACTS.WORKFLOW_FACTS__shared.UnsupportedReuse': {'private': ['parent']},
                      'WORKFLOW_FACTS.WORKFLOW_FACTS__shared.find_reuse_region': {'private': ['parent']},
                      'WORKFLOW_FACTS.WORKFLOW_FACTS__shared.lower_reuse': {'private': ['parent']},
                      'RESOLUTION.analysis_inputs.analysis_inputs': {'private': ['parent']},
                      'RESOLUTION.graph_inputs._git_selection_witness': {'private': ['parent']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._RESOLUTION_INPUTS': {'private': ['parent',
                                                                                               'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'STATE_ANALYSIS.STATE_ANALYSIS__shared._SourceVersionChanged': {'private': ['parent']},
                      'STATE_ANALYSIS.STATE_ANALYSIS__shared._read': {'private': ['parent']},
                      'SOURCE_CAPTURE.web_imports.lookup_web': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'SOURCE_CAPTURE.SOURCE_CAPTURE__shared._discover': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'STATE_ANALYSIS.STATE_ANALYSIS__shared._CHECKER': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'STATE_ANALYSIS.STATE_ANALYSIS__shared._LANGUAGES': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'SOURCE_CAPTURE.web_imports._FRONTEND': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'SOURCE_CAPTURE.web_imports._SCANNER': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'SOURCE_CAPTURE.web_imports.scan_web': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'STATE_ANALYSIS.WEB_STATE.WEB_STATE__shared._SCANNER': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'trace_bindings.native_trace_snapshot': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'realization_graph_cli._options': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/RESOLUTION']},
                      'SOURCE_CAPTURE.source_parser.ImportSite': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/native_projection']},
                      'SOURCE_CAPTURE.source_parser.Source': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/native_projection']},
                      'SOURCE_CAPTURE.source_paths.excluded_source_path': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/KERNEL_MIXER_C59/kernel_services/realization_audit']},
                      'FEATURE_IMPORT_GRAPH_C61__tests.FEATURE_IMPORT_GRAPH_C61__tests__shared.run_provider': {'private': ['LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IMPORT_GRAPH_C61/FEATURE_IMPORT_GRAPH_C61__tests/realization']}}},
 'io': {'server': {'build_graph': {'transport': 'cli',
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
                   'import_ownership': {'transport': 'cli',
                                        'runner': 'managed_python',
                                        'module': 'LAYER_4_ENGINE_STUDIO_C14.IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.import_ownership',
                                        'arguments': ['<project-root>']},
                   'workflow_spec': {'transport': 'cli',
                                     'runner': 'managed_python',
                                     'module': 'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.workflow_spec',
                                     'arguments': ['<solution-atom>', 'render or check <trace>'],
                                     'output': 'Mermaid or a JSON flow check'},
                   'workflow_reuse': {'transport': 'cli',
                                      'runner': 'managed_python',
                                      'module': 'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.workflow_reuse',
                                      'input_fields': ['root',
                                                       'control_root',
                                                       'graph',
                                                       'structure',
                                                       'caller',
                                                       'callee'],
                                      'optional_paired_inputs': ['first', 'last'],
                                      'output': 'JSON reuse finding'}},
        'client': [{'transport': 'cli',
                    'optional': True,
                    'command': ['lean', '--run', 'WorkflowTrace.lean'],
                    'input': 'JSON workflow model and trace'},
                   {'transport': 'cli',
                    'optional': True,
                    'command': ['lean', '--run', 'FlowComparison.lean'],
                    'input': 'JSON pair of source-derived effect sequences'},
                   {'transport': 'cli',
                    'optional': True,
                    'command': ['lean', '--run', 'ActionEffects.lean'],
                    'input': 'JSON batch of ordered state cases on stdin'},
                   {'transport': 'cli',
                    'optional': True,
                    'command': ['node',
                                'LAYER_4_ENGINE_STUDIO_C14/IWE_CONSOLE_C43/APP_IWE_CONSOLE/FEATURE_IWE_CONSOLE_FRONTEND/scripts/import-graph-scanner.ts'],
                    'input': 'JSON source batch on stdin'}]},
 'state': {'reads': ['admitted Project source inventory',
                     'dependency manifests',
                     'Git ignore metadata',
                     'installed Python distribution metadata'],
           'writes': []}}
```

## Component Contract

### Resolve authored source relationships

#### Guarantee

Given a Project root and its Python import roots, capture and resolve static
Python imports without executing the analyzed Modules. Each import occurrence
records its source location and either its resolved target or its resolution
status.

When the framework-local parsers are installed, resolve JavaScript,
TypeScript, and Svelte imports without running Project source or config.
Report files as unsupported when the parsers are unavailable.

Link a direct `<package>__tests` directory to the named owner when that owner
resolves in the Project.

The Graph build CLI returns the resolved rows and read issues as JSON.
When it receives the attested Structure, it can resolve Test Packages
to the declared Components they exercise. Report Code Access denials,
uncertain imports, and declared or undeclared owner bypasses from the
captured import sites and declared Package ownership.
Kernel owns publication of the accepted graph.

The ownership check follows named, statically resolved symbols to their
defining Package. Report a forwarding import when the named provider
belongs to a different Package. Allow an entry to expose its own
implementation. The static check requires the reviewed parsers for
each web source it checks.

Compare ordered outputs and side effects from aligned, complete flow
traces in Lean. Report the first difference. Mark incomplete evidence
unresolved. Keep the search prompt with the Lean checker.

Compile a formal workflow from a Tier 1 Solution. Reject overlapping
guards for the same event in one state and states with no path to a
final state. Render every valid transition in Mermaid. Check a complete
recorded flow against the same workflow in Lean.

Report witnessed state access and silent paths for supported code.
Return source evidence and mark incomplete analysis unresolved.

#### References

AN-S-3082 and AN-T-2947.
