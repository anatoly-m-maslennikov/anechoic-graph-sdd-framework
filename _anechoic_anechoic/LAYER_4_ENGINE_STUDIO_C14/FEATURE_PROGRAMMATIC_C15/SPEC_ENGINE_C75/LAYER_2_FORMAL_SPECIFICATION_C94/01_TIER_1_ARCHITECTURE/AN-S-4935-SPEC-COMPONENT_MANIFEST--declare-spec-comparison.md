---
atom_family: SPEC
atom_id: AN-S-4935
container:
  component: C94
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: "2026-11-28T14:03:07+00:00"
---
## Summary

Declare Spec Comparison

## Purpose

Compare Manifest to Contract, Manifest to Solution, and Contract to Solution using the formal model.

## Component Identity

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest
declare_entity(entity_name='Component Manifest', instance=ComponentManifest(component_id='C88', layer=4, name='Spec Comparison', lens_whitelist=['DES', 'SPEC']))
```

## Component Boundaries

```python
{'code': {'imports': ['C83',
                      'C84',
                      'C85',
                      'C87',
                      'C88',
                      'C90',
                      'top_down__pub.compare_obligations',
                      'contract_model._package__shared.HTTP_CHECKS',
                      '_package__shared.report_comparison',
                      '_package__shared._operation_claims'],
          'exports': {'tool_obligations.tool_api_obligations__shared': {'shared': ['C88']},
                      'group_comparison.group_spec__shared': {'shared': ['C88']},
                      'top_down__pub.compare_obligations': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_SPEC_COMPARISON_C88/trace_facts_impl',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_SPEC_COMPARISON_C88/group_comparison']},
                      'tool_response.facts__shared._delivery_coverage': {'shared': ['C88']},
                      'tool_response.facts__shared._derived': {'shared': ['C88']},
                      'tool_response.facts__shared._error_facts': {'shared': ['C88']},
                      'tool_response.facts__shared._outcome_facts': {'shared': ['C88']},
                      'tool_response.facts__shared._record': {'shared': ['C88']},
                      'tool_response.facts__shared._response_coverage': {'shared': ['C88']},
                      'tool_response.facts__shared._terminal_facts': {'shared': ['C88']},
                      '_package__shared.feasible_terminals': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.compare_trace_values': {'shared': ['C75',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                           'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace_values']},
                      '_package__shared._binding_directions': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/contracts/model',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace_spec']},
                      '_package__shared._cli_profiles': {'shared': ['C89']},
                      '_package__shared._dispatch_facts': {'shared': ['C89']},
                      '_package__shared._initial_trigger': {'shared': ['C89']},
                      '_package__shared._manifest_binding': {'shared': ['C89',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/manifest']},
                      '_package__shared._manifest_contract': {'shared': ['C89',
                                                                         'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                         'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace_spec']},
                      '_package__shared._manifest_endpoint': {'shared': ['C89']},
                      '_package__shared._operation_claims': {'shared': ['C75',
                                                                        'C89',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_SPEC_COMPARISON_C88/cli_facts']},
                      '_package__shared._outcome_stdout': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared._solution_binding': {'shared': ['C89']},
                      '_package__shared._tool_contract': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons']},
                      '_package__shared._tool_solution': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons']},
                      '_package__shared._uncovered_outcomes': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace']},
                      '_package__shared._workflow_facts': {'shared': ['C89',
                                                                      'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      '_package__shared.check_cli_spec': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons/framing',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/contracts/dispatch',
                                                                     'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/contracts/model']},
                      '_package__shared.check_group_spec': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/integration']},
                      '_package__shared.check_shape_spec': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/contracts/shape']},
                      '_package__shared.check_tool_api_spec': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons/framing']},
                      '_package__shared.check_trace_spec': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons/framing',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/contracts/dispatch',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/contracts/model',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/contracts/shape',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace',
                                                                       'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace_spec']},
                      '_package__shared.compare_delegation': {'shared': ['C89']},
                      '_package__shared.compare_obligations': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons/renderer',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons/scope',
                                                                          'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/contracts/shape']},
                      '_package__shared.compare_cli_spec': {'shared': ['C75']},
                      '_package__shared.compare_shape_spec': {'shared': ['C75']},
                      '_package__shared.compare_tool_api_spec': {'shared': ['C75']},
                      '_package__shared.compare_trace_spec': {'shared': ['C75']},
                      '_package__shared.compare_trace_workflow': {'shared': ['C89',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons/diagnostic',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/comparisons/renderer',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace_spec',
                                                                             'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/trace_values']},
                      '_package__shared.manifest_tool_api': {'shared': ['C74',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional',
                                                                        'LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional/workflows/manifest']},
                      '_package__shared.solution_tool_api': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/SPEC_ENGINE_C75__tests/functional']},
                      'cli_facts._package__shared._BINDING_FIELDS': {'shared': ['C88']},
                      'cli_facts._package__shared._manifest_facts': {'shared': ['C88']},
                      'cli_facts._package__shared._common_checks': {'shared': ['C88']},
                      'cli_facts._package__shared._first_dispatch': {'shared': ['C88']},
                      'cli_facts._package__shared._query_checks': {'shared': ['C88']},
                      'cli_facts._package__shared._reachable_without': {'shared': ['C88']},
                      'cli_facts._package__shared._release_checks': {'shared': ['C88']},
                      'cli_facts._package__shared._solution_outcomes': {'shared': ['C88']},
                      'cli_facts._package__shared._success_outputs': {'shared': ['C88']},
                      'cli_facts._package__shared': {'shared': ['C88']},
                      'trace_facts_impl._package__shared.compare_http_workflow': {'shared': ['C88']},
                      'trace_facts_impl._package__shared.trace_claims': {'shared': ['C88']},
                      'trace_facts_impl._package__shared.workflow_facts': {'shared': ['C88']},
                      'trace_facts_impl._package__shared': {'shared': ['C88']},
                      '_package__shared.report_comparison': {'shared': ['LAYER_4_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/SPEC_ENGINE_C75/LAYER_2_FORMAL_SPECIFICATION_C94/LAYER_4_SPEC_COMPARISON_C88/group_comparison']}}},
 'io': {'server': {'compare_obligations': {'outcomes': {'compared': {'must_effect': [('C88.manifest_contract',
                                                                                      'compared'),
                                                                                     ('C88.manifest_solution',
                                                                                      'compared'),
                                                                                     ('C88.contract_solution',
                                                                                      'compared')]}}}}}}
```

## Component Contract

```python trace
declare_trace_contract(
    action='compare_obligations',
    output='compared',
    must_effect=(('C88.manifest_contract', 'compared'),
                 ('C88.manifest_solution', 'compared'),
                 ('C88.contract_solution', 'compared')),
)
```
