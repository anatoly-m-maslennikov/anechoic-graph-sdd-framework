---
atom_family: SPEC
atom_id: AN-S-4911
container:
  component: C75
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4910@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T13:37:33Z'
---

## Summary

Compare pinned Specs through one formal model.

## Claim

### Formal Claim

```python
component_workflow(
    component='C75',
    action='verify_formal_chain',
    machine={
        'id': 'c75_verify_formal_chain',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'spec_chain_requested': {'target': 'checking', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'trigger'}}},
            }},
            'checking': {'on': {
                'declarations_and_links_validated': {'target': 'normalizing', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C83.pinned_sources', 'outcome': 'loaded',
                               'detail': {'component': 'C83', 'action': 'load_boundary_model', 'output': 'loaded'}}}},
                'source_finding_formed': {'target': 'reporting_diagnostics', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C90.source_diagnostic', 'outcome': 'formed',
                               'detail': {'component': 'C90', 'action': 'finding', 'output': 'reported'}}}},
                'checking_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'normalizing': {'on': {
                'common_model_built': {'target': 'generating_lean', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C85.formal_declarations', 'outcome': 'normalized',
                               'detail': {'component': 'C85', 'action': 'normalize_spec', 'output': 'normalized', 'model': 'request_normalized_model'}}}},
                'normalizing_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'generating_lean': {'on': {
                'lean_generated': {'target': 'validating_translation', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C84.lean_source', 'outcome': 'generated',
                               'detail': {'component': 'C84', 'action': 'compile_lean', 'output': 'compiled', 'model': 'request_normalized_model'}}}},
                'generating_lean_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'validating_translation': {'on': {
                'lean_declarations_validated': {'target': 'rendering', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C86.lean_declarations', 'outcome': 'validated',
                               'detail': {'component': 'C86', 'action': 'validate_translation', 'output': 'matched', 'model': 'request_normalized_model'}}}},
                'validating_translation_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
                'unsupported_comparison_finding_formed': {'target': 'reporting_diagnostics', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C90.source_diagnostic', 'outcome': 'formed',
                               'detail': {'component': 'C90', 'action': 'finding', 'output': 'reported'}}}},
                'translation_conflicting': {'target': 'reporting_diagnostics', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C86.translation_findings', 'outcome': 'reported',
                               'detail': {'component': 'C86', 'action': 'validate_translation', 'output': 'conflicting'}}}},
                'translation_unresolved': {'target': 'reporting_diagnostics', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C86.translation_findings', 'outcome': 'reported',
                               'detail': {'component': 'C86', 'action': 'validate_translation', 'output': 'unresolved'}}}},
            }},
            'rendering': {'on': {
                'mermaid_generated': {'target': 'comparing', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C87.mermaid_diagram', 'outcome': 'rendered',
                               'detail': {'component': 'C87', 'action': 'render_solution', 'output': 'rendered', 'model': 'request_normalized_model'}}}},
                'rendering_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'comparing': {'on': {
                'manifest_contract_compared': {'target': 'checking_manifest_solution', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C88.manifest_contract', 'outcome': 'compared',
                               'detail': {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}}}},
                'comparing_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'checking_manifest_solution': {'on': {
                'manifest_solution_compared': {'target': 'checking_contract_solution', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C88.manifest_solution', 'outcome': 'compared',
                               'detail': {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}}}},
                'checking_manifest_solution_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'checking_contract_solution': {'on': {
                'contract_solution_compared': {'target': 'reporting', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C88.contract_solution', 'outcome': 'compared',
                               'detail': {'component': 'C88', 'action': 'compare_obligations', 'output': 'compared'}}}},
                'checking_contract_solution_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'reporting': {'on': {
                'comparison_reported': {'target': 'returning', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.comparison_complete', 'outcome': 'reported'}}},
            }},
            'reporting_diagnostics': {'on': {
                'translation_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'incomplete': {'on': {
                'diagnostics_returned': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'incomplete'}}},
            }},
            'returning': {'on': {
                'comparison_returned': {'target': 'done', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'output', 'outcome': 'compared'}}},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
