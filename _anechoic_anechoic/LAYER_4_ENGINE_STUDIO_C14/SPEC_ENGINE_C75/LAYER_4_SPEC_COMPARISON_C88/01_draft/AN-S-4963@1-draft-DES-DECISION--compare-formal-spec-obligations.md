---
atom_family: SPEC
atom_id: AN-S-4963
container:
  component: C88
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4962@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:35:58.956802+00:00'
---

## Summary

Compare formal Spec obligations.

## Claim

### Prose Claim

Compare the role obligations through the formal model and report the results for all three directions before returning.

### Formal Claim

```python
component_workflow(
    component='C88',
    action='compare_obligations',
    machine={'id': 'c88_compare_obligations',
 'initial': 'idle',
 'states': {'idle': {'on': {'requested': {'target': 'checking',
                                          'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'checking': {'on': {'manifest_contract_compared': {'target': 'checking_manifest_solution',
                                                    'guard': {'type': 'matchesTrace',
                                                              'params': {'kind': 'effect',
                                                                         'target': 'C88.manifest_contract',
                                                                         'outcome': 'compared'}}}}},
            'checking_manifest_solution': {'on': {'manifest_solution_compared': {'target': 'checking_contract_solution',
                                                    'guard': {'type': 'matchesTrace',
                                                              'params': {'kind': 'effect',
                                                                         'target': 'C88.manifest_solution',
                                                                         'outcome': 'compared'}}}}},
            'checking_contract_solution': {'on': {'contract_solution_compared': {'target': 'return_compared',
                                                    'guard': {'type': 'matchesTrace',
                                                              'params': {'kind': 'effect',
                                                                         'target': 'C88.contract_solution',
                                                                         'outcome': 'compared'}}}}},
            'done': {'type': 'final'},
            'return_compared': {'on': {'compared_returned': {'target': 'done',
                                                             'guard': {'type': 'matchesTrace',
                                                                       'params': {'kind': 'output',
                                                                                  'outcome': 'compared'}}}}}}},
)
```
