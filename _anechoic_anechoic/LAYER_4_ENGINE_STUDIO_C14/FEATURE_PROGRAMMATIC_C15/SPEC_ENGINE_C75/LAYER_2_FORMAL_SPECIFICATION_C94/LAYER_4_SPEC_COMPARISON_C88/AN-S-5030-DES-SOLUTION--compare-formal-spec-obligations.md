---
atom_family: SPEC
atom_id: AN-S-5030
container:
  component: C88
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS: [AN-S-4935@1]
state:
  status: active
  version: 1
  updated_at: '2026-11-26T23:29:03+00:00'
---

## Summary

Compare formal spec obligations

## Claim

Compare the role obligations through the formal model and report the results for all three directions before returning.

### Formal Claim

```python
component_workflow(
    component='C88',
    action='compare_obligations',
    machine={'id': 'compare_obligations',
 'initial': 'idle',
 'states': {'idle': {'on': {'request': {'to': 'step0', 'expect': {'kind': 'trigger'}}}},
            'step0': {'on': {'effect0': {'to': 'step1',
                                         'expect': {'kind': 'effect',
                                                    'target': 'C88.manifest_contract',
                                                    'outcome': 'compared'}}}},
            'step1': {'on': {'effect1': {'to': 'step2',
                                         'expect': {'kind': 'effect',
                                                    'target': 'C88.manifest_solution',
                                                    'outcome': 'compared'}}}},
            'step2': {'on': {'effect2': {'to': 'step3',
                                         'expect': {'kind': 'effect',
                                                    'target': 'C88.contract_solution',
                                                    'outcome': 'compared'}}}},
            'step3': {'on': {'return': {'to': 'done',
                                        'expect': {'kind': 'output',
                                                   'outcome': 'compared'}}}},
            'done': {'type': 'final'}}},
)
```
