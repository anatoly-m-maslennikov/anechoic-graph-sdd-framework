---
atom_family: SPEC
atom_id: AN-S-5035
concern:
  subject: "Solution"
  path: "Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification"
  relation: "is_narrower_than"
container:
  component: C94
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-5020@5
state:
  status: active
  version: 6
  updated_at: "2026-11-27T16:19:44.298791+00:00"
---
## Summary

Verify a pinned formal chain

## Claim

### Formal Claim

```python
component_workflow(component='C94', action='verify_pinned_specs', machine={
    'id': 'c94_verify_pinned_specs', 'initial': 'read', 'states': {
        'read': {'on': {
            'load_pins': {'to': 'generate', 'expect': {'kind': 'effect', 'detail': {'component': 'C83', 'action': 'load_boundary_model', 'output': 'loaded', 'manifest': 'AN-S-4930@2'}, 'target': 'C83.pinned_sources', 'outcome': 'loaded',
                'bind': {'sources': 'source_set'}}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'generate': {'on': {
            'translate': {'to': 'validate', 'expect': {'kind': 'effect', 'detail': {'component': 'C84', 'action': 'compile_lean', 'output': 'compiled', 'manifest': 'AN-S-4931@1'}, 'target': 'C84.lean_source', 'outcome': 'generated',
                'bind': {'selected_model': 'model_pin'}}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'validate': {'on': {
            'validate_translation': {'to': 'accept', 'expect': {'kind': 'effect', 'detail': {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'manifest': 'AN-S-4933@1',
                           'model': 'request_normalized_model'},
                'target': 'C86.lean_declarations', 'outcome': 'validated',
                'same_as': {'model_pin': 'selected_model'}}},
            'validate_framing': {'to': 'accept_framing', 'expect': {'kind': 'effect',
                'target': 'C86.framing_comparison', 'outcome': 'reported',
                'same_as': {'model_pin': 'selected_model'},
                'bind': {'finite_result': 'framing_result_pin'},
                'detail': {'component': 'C86', 'action': 'validate_translation',
                           'output': 'bounded_match', 'manifest': 'AN-S-4933@1'}}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'accept': {'on': {'accepted': {'to': 'render', 'expect': {
            'kind': 'effect', 'target': 'C94.translation', 'outcome': 'accepted',
            'same_as': {'model_pin': 'selected_model'},
            'bind': {'selected_solution': 'solution_pin'}}}}},
        'accept_framing': {'on': {'accepted': {'to': 'render_framing', 'expect': {
            'kind': 'effect', 'target': 'C94.translation', 'outcome': 'accepted',
            'same_as': {'model_pin': 'selected_model'},
            'bind': {'selected_solution': 'solution_pin'}}}}},
        'render_framing': {'on': {'render': {'to': 'report_framing',
            'expect': {'kind': 'effect',
            'target': 'C87.mermaid_diagram', 'outcome': 'rendered',
            'same_as': {'solution_pin': 'selected_solution'},
            'detail': {'component': 'C87', 'action': 'render_solution',
                       'output': 'rendered', 'manifest': 'AN-S-4934@1'}}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}}}},
        'render': {'on': {
            'render': {'to': 'compare', 'expect': {'kind': 'effect', 'detail': {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'manifest': 'AN-S-4934@1'}, 'target': 'C87.mermaid_diagram', 'outcome': 'rendered',
                'same_as': {'solution_pin': 'selected_solution'}}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'compare': {'on': {
            'compare': {'to': 'report', 'expect': {'kind': 'effect', 'detail': {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared', 'manifest': 'AN-S-4935@1'}, 'target': 'C88.manifest_solution', 'outcome': 'compared',
                'same_as': {'model_pin': 'selected_model'}}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'report': {'on': {'ready': {'to': 'return', 'expect': {
            'kind': 'effect', 'target': 'C94.formal_verification',
            'outcome': 'compared',
            'same_as': {'source_set': 'sources', 'model_pin': 'selected_model'}}}}},
        'report_framing': {'on': {'ready': {'to': 'return', 'expect': {
            'kind': 'effect', 'target': 'C94.formal_verification',
            'outcome': 'compared',
            'same_as': {'source_set': 'sources', 'model_pin': 'selected_model',
                        'framing_result_pin': 'finite_result'}}}}},
        'return': {'on': {'result': {'to': 'end', 'expect': {
            'kind': 'output', 'outcome': 'compared',
            'same_as': {'model_pin': 'selected_model'}}}}},
        'diagnose': {'on': {'incomplete': {'to': 'end', 'expect': {
            'kind': 'output', 'outcome': 'incomplete'}}}},
        'end': {'type': 'final'},
    },
})
```

```python
component_workflow(component='C94', action='generate_pinned_cases', machine={
    'id': 'c94_generate_pinned_cases', 'initial': 'generate', 'states': {
        'generate': {'on': {
            'derive': {'to': 'publish', 'expect': {'kind': 'effect',
                'target': 'test_cases', 'outcome': 'derived',
                'detail': {'component': 'C92', 'action': 'generate_framing_cases',
                           'output': 'generated', 'manifest': 'AN-S-5016@1',
                           'interface': 'framing_cases', 'transport': 'in_process'}}},
            'invalid': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'invalid'}},
        }},
        'publish': {'on': {'ready': {'to': 'return', 'expect': {
            'kind': 'effect', 'target': 'C94.generated_cases',
            'outcome': 'ready'}}}},
        'return': {'on': {'result': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'generated'}}}},
        'end': {'type': 'final'},
    },
})
```

## Semantics

Keep exact source references and digests separate from the normalized
Model pin. Compare the generated claims with the exact claims and sources
evaluated in Lean. Preserve that Model identity through C88 comparison.

C87 receives the selected Solution projection and verifies its digest and
Action. For bounded framing, preserve the digest of the claims and the
finite result from C86. An incomplete result identifies the affected
source and failing field or stage.

The Spec Engine generation entry calls C92 in process and returns its
report with the source pins intact. This return makes the C94 cases ready.
