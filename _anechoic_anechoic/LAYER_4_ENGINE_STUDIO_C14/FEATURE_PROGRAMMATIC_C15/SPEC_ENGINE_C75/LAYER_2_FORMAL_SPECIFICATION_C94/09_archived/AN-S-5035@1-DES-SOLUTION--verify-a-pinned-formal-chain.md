---
atom_family: SPEC
atom_id: AN-S-5035
container:
  component: C94
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-5020@3
state:
  status: "archived"
  version: 1
  updated_at: '2026-11-26T23:28:14.968347+00:00'
---
## Summary

Verify a pinned formal chain

## Claim

### Prose Claim

Read the pinned declarations through Spec Reading. Retain the exact refs
and digests. Generate and validate
Lean. Render the validated Solution. Compare ordinary declarations through
C88. For bounded framing, report the finite comparison from C86.
Return the same source pins and normalized Model identity with the result.
If an input or check prevents comparison, report the source and failing
field or stage before returning incomplete.

### Formal Claim

```python
component_workflow(component='C94', action='verify_pinned_specs', machine={
    'id': 'c94_verify_pinned_specs', 'initial': 'read', 'states': {
        'read': {'on': {
            'load_pins': {'to': 'generate', 'expect': {'kind': 'effect', 'detail': {'component': 'C83', 'action': 'load_boundary_model', 'output': 'loaded', 'manifest': 'AN-S-4930@1-draft'}, 'target': 'C83.pinned_sources', 'outcome': 'loaded'}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'generate': {'on': {
            'translate': {'to': 'validate', 'expect': {'kind': 'effect', 'detail': {'component': 'C84', 'action': 'compile_lean', 'output': 'compiled', 'manifest': 'AN-S-4931@1-draft'}, 'target': 'C84.lean_source', 'outcome': 'generated'}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'validate': {'on': {
            'validate_translation': {'to': 'accept', 'expect': {'kind': 'effect', 'detail': {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'manifest': 'AN-S-4933@1-draft'}, 'target': 'C86.lean_declarations', 'outcome': 'validated'}},
            'validate_framing': {'to': 'accept_framing', 'expect': {'kind': 'effect',
                'target': 'C86.framing_comparison', 'outcome': 'reported',
                'detail': {'component': 'C86', 'action': 'validate_translation',
                           'output': 'bounded_match', 'manifest': 'AN-S-4933@1-draft'}}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'accept': {'on': {'accepted': {'to': 'render', 'expect': {
            'kind': 'effect', 'target': 'C94.translation', 'outcome': 'accepted'}}}},
        'accept_framing': {'on': {'accepted': {'to': 'render_framing', 'expect': {
            'kind': 'effect', 'target': 'C94.translation', 'outcome': 'accepted'}}}},
        'render_framing': {'on': {'render': {'to': 'report', 'expect': {'kind': 'effect',
            'target': 'C87.mermaid_diagram', 'outcome': 'rendered',
            'detail': {'component': 'C87', 'action': 'render_solution',
                       'output': 'rendered', 'manifest': 'AN-S-4934@1-draft'}}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}}}},
        'render': {'on': {
            'render': {'to': 'compare', 'expect': {'kind': 'effect', 'detail': {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'manifest': 'AN-S-4934@1-draft'}, 'target': 'C87.mermaid_diagram', 'outcome': 'rendered'}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'compare': {'on': {
            'compare': {'to': 'report', 'expect': {'kind': 'effect', 'detail': {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared', 'manifest': 'AN-S-4935@1-draft'}, 'target': 'C88.manifest_solution', 'outcome': 'compared'}},
            'error': {'to': 'diagnose', 'expect': {'kind': 'effect',
                'target': 'C94.source_diagnostic', 'outcome': 'reported'}},
        }},
        'report': {'on': {'ready': {'to': 'return', 'expect': {
            'kind': 'effect', 'target': 'C94.formal_verification', 'outcome': 'compared'}}}},
        'return': {'on': {'result': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'compared'}}}},
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
            'derive': {'to': 'admit', 'expect': {'kind': 'effect',
                'target': 'test_cases', 'outcome': 'derived',
                'detail': {'component': 'C92', 'action': 'generate_framing_cases',
                           'output': 'generated', 'manifest': 'AN-S-5016@1-draft',
                           'interface': 'framing_cases', 'transport': 'in_process'}}},
            'invalid': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'invalid'}},
        }},
        'admit': {'on': {'ready': {'to': 'return', 'expect': {'kind': 'effect',
            'target': 'C94.generated_cases', 'outcome': 'ready'}}}},
        'return': {'on': {'result': {'to': 'end', 'expect': {'kind': 'output', 'outcome': 'generated'}}}},
        'end': {'type': 'final'},
    },
})
```
