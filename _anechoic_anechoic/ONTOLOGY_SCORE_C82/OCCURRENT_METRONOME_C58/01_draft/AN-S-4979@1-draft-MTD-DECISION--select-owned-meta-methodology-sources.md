---
atom_family: SPEC
atom_id: AN-S-4979
container:
  component: C58
tier: 1
context:
  template: DECISION
  lens: DOM/MTD
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:46:13.372267+00:00'
relations:
  IS_SOLUTION_FOR:
  - AN-S-4978@1-draft
---

## Summary

Select owned meta-methodology sources.

## Claim

Select the Active declaration carriers contained by C58.
Expose the carriers to the consumer as authored sources.

### Formal Claim

```python
component_workflow(
    component='C58',
    action='provide_meta_methodology_sources',
    machine={'id': 'provide_meta_methodology_sources',
     'initial': 'idle',
     'states': {'idle': {'on': {'select_published_sources': {'target': 'selecting',
                                                             'guard': {'type': 'matchesTrace',
                                                                       'params': {'kind': 'trigger'}}}}},
                'selecting': {'on': {'owned_sources_available': {'target': 'reporting',
                                                                 'guard': {'type': 'matchesTrace',
                                                                           'params': {'kind': 'effect',
                                                                                      'target': 'C58.meta_methodology',
                                                                                      'outcome': 'available'}}}}},
                'reporting': {'on': {'return_sources': {'target': 'done',
                                                        'guard': {'type': 'matchesTrace',
                                                                  'params': {'kind': 'output',
                                                                             'outcome': 'declarations_available'}}}}},
                'done': {'type': 'final'}}},
)
```
