---
atom_family: SPEC
atom_id: AN-S-4965
container:
  component: C89
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4964@1-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:35:58.956802+00:00'
---

## Summary

Check a delegated child or sibling outcome.

## Claim

### Prose Claim

Load the selected parent effect and pinned child Specs, check the child relationship, compare the declared and modeled outcome, and report the result. For a sibling, check the declared relationship and client interface against the selected event, provider Manifest, and any explicit provider bindings. Compare through C88.compare_delegation and report the result.

### Formal Claim

```python
component_workflow(
    component='C89',
    action='check_child_outcome',
    machine={'id': 'c89_check_child_outcome',
 'initial': 'idle',
 'states': {'idle': {'on': {'requested': {'target': 'checking',
                                          'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'checking': {'on': {'compared_effect': {'target': 'return_compared',
                                                    'guard': {'type': 'matchesTrace',
                                                              'params': {'kind': 'effect',
                                                                         'target': 'C89.child_outcome_comparison',
                                                                         'outcome': 'reported'}}}}},
            'done': {'type': 'final'},
            'return_compared': {'on': {'compared_returned': {'target': 'done',
                                                             'guard': {'type': 'matchesTrace',
                                                                       'params': {'kind': 'output',
                                                                                  'outcome': 'compared'}}}}}}},
)
```

```python
component_workflow(
    component='C89',
    action='check_sibling_outcome',
    machine={'id': 'c89_check_sibling_outcome',
 'initial': 'idle',
 'states': {'idle': {'on': {'requested': {'target': 'checking',
                                          'guard': {'type': 'matchesTrace', 'params': {'kind': 'trigger'}}}}},
            'checking': {'on': {'compared_effect': {'target': 'return_compared',
                                                    'guard': {'type': 'matchesTrace',
                                                              'params': {'kind': 'effect',
                                                                         'target': 'C89.sibling_outcome_comparison',
                                                                         'outcome': 'reported'}}}}},
            'done': {'type': 'final'},
            'return_compared': {'on': {'compared_returned': {'target': 'done',
                                                             'guard': {'type': 'matchesTrace',
                                                                       'params': {'kind': 'output',
                                                                                  'outcome': 'compared'}}}}}}},
)
```
