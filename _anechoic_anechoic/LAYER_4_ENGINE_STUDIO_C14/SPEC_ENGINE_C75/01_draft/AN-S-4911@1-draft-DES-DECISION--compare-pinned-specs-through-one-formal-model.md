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
                    'params': {'kind': 'effect', 'target': 'C75.sources', 'outcome': 'validated'}}},
                'source_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'normalizing': {'on': {
                'common_model_built': {'target': 'generating_lean', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.model', 'outcome': 'normalized'}}},
                'model_diagnostics_reported': {'target': 'incomplete', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.diagnostics', 'outcome': 'reported'}}},
            }},
            'generating_lean': {'on': {
                'lean_generated': {'target': 'rendering', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.lean', 'outcome': 'generated'}}},
            }},
            'rendering': {'on': {
                'mermaid_generated': {'target': 'comparing', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.mermaid', 'outcome': 'generated'}}},
            }},
            'comparing': {'on': {
                'manifest_contract_compared': {'target': 'checking_manifest_solution', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.manifest_contract', 'outcome': 'compared'}}},
            }},
            'checking_manifest_solution': {'on': {
                'manifest_solution_compared': {'target': 'checking_contract_solution', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.manifest_solution', 'outcome': 'compared'}}},
            }},
            'checking_contract_solution': {'on': {
                'contract_solution_compared': {'target': 'reporting', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.contract_solution', 'outcome': 'compared'}}},
            }},
            'reporting': {'on': {
                'comparison_reported': {'target': 'returning', 'guard': {'type': 'matchesTrace',
                    'params': {'kind': 'effect', 'target': 'C75.comparison_complete', 'outcome': 'reported'}}},
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
