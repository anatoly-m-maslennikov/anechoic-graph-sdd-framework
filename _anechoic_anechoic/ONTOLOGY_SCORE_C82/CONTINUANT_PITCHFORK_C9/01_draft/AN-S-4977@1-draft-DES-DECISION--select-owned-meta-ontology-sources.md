---
atom_family: SPEC
atom_id: AN-S-4977
container:
  component: C9
tier: 1
context:
  template: DECISION
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T21:46:13.372267+00:00'
relations:
  IS_SOLUTION_FOR:
  - AN-S-4976@1-draft
---

## Summary

Select owned meta-ontology sources.

## Claim

Select the Active declaration carriers contained by C9.
Expose the carriers to the consumer as authored sources.

### Formal Claim

```python
component_workflow(
    component='C9',
    action='provide_meta_ontology_sources',
    machine={'id': 'provide_meta_ontology_sources',
     'initial': 'idle',
     'states': {'idle': {'on': {'select_published_sources': {'target': 'selecting',
                                                             'guard': {'type': 'matchesTrace',
                                                                       'params': {'kind': 'trigger'}}}}},
                'selecting': {'on': {'owned_sources_available': {'target': 'reporting',
                                                                 'guard': {'type': 'matchesTrace',
                                                                           'params': {'kind': 'effect',
                                                                                      'target': 'C9.meta_ontology',
                                                                                      'outcome': 'available'}}}}},
                'reporting': {'on': {'return_sources': {'target': 'done',
                                                        'guard': {'type': 'matchesTrace',
                                                                  'params': {'kind': 'output',
                                                                             'outcome': 'declarations_available'}}}}},
                'done': {'type': 'final'}}},
)
```
