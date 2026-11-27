---
atom_family: SPEC
atom_id: AN-S-5075
container:
  component: C91
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-4809@7-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T17:00:30.949693+00:00'
---
## Summary

Describe shared beta Tool HTTP with OpenAPI

## Claim

### Prose Claim

Project the C91 descriptors into the catalog and named invocation branches. Use the shared request model for the HTTP envelope. Evaluate Project admission in the live Backend and return the declared result or typed error.

### Formal Claim

```python
component_workflow(
    component='C91',
    action='listTools',
    machine={'id': 'c91_openapi_catalog',
 'initial': 'idle',
 'states': {'idle': {'on': {'request': {'to': 'return',
                                        'expect': {'kind': 'trigger',
                                                   'detail': {'endpoint': 'GET '
                                                                          '/tools',
                                                              'route_name': 'catalog'}}}}},
            'return': {'on': {'listed': {'to': 'done',
                                         'expect': {'kind': 'output',
                                                    'outcome': 'listed',
                                                    'detail': {'status_code': 200,
                                                               'envelope': 'result'}}}}},
            'done': {'type': 'final'}}},
)
```

```python
component_workflow(
    component='C91',
    action='invokeTool',
    machine={'id': 'c91_openapi_invoke',
 'initial': 'idle',
 'states': {'idle': {'on': {'request': {'to': 'return',
                                        'expect': {'kind': 'trigger',
                                                   'detail': {'endpoint': 'POST '
                                                                          '/tools',
                                                              'route_name': 'invoke'}}}}},
            'return': {'on': {'accepted': {'to': 'done',
                                           'expect': {'kind': 'output',
                                                      'outcome': 'accepted',
                                                      'detail': {'status_code': 200,
                                                                 'envelope': 'result'}}},
                              'refused': {'to': 'done',
                                          'expect': {'kind': 'output',
                                                     'outcome': 'refused',
                                                     'detail': {'status_code': 200,
                                                                'envelope': 'typed_error'}}},
                              'unavailable': {'to': 'done',
                                              'expect': {'kind': 'output',
                                                         'outcome': 'unavailable',
                                                         'detail': {'status_code': 503,
                                                                    'envelope': 'typed_error'}}}}},
            'done': {'type': 'final'}}},
)
```
