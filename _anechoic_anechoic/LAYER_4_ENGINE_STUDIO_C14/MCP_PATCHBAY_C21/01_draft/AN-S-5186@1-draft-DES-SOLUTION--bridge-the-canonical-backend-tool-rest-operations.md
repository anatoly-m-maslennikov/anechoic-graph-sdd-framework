---
atom_family: SPEC
atom_id: AN-S-5186
container:
  component: C21
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3044@70-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T18:02:38.116327+00:00'
---

## Summary

Bridge the canonical Backend Tool REST operations

## Claim

### Prose Claim

The shared host and the MCP transport use the C91 catalog and invocation.
Use the admitted Project client in direct mode. Return the Backend
envelope after checking its shape and Project receipt. Reject an invalid
public request at the transport boundary before calling the Backend.

### Formal Claim

```python
component_workflow(
    component='C21',
    action='forward_tool_rest',
    machine={'id': 'c21_tool_rest',
 'initial': 'idle',
 'states': {'idle': {'on': {'shared_catalog': {'to': 'shared_catalog',
                                               'expect': {'kind': 'trigger'}},
                            'shared_invocation': {'to': 'shared_invocation',
                                                  'expect': {'kind': 'trigger'}},
                            'direct_catalog': {'to': 'direct_catalog',
                                               'expect': {'kind': 'trigger'}},
                            'direct_invocation': {'to': 'direct_invocation',
                                                  'expect': {'kind': 'trigger'}},
                            'invalid_transport_request': {'to': 'done',
                                                          'expect': {'kind': 'output',
                                                                     'outcome': 'transport_refused'}}}},
            'shared_catalog': {'on': {'backend_operation': {'to': 'shared_catalog_response',
                                                            'expect': {'kind': 'effect',
                                                                       'target': 'C91.shared_api',
                                                                       'outcome': 'catalog',
                                                                       'detail': {'endpoint': 'GET '
                                                                                              '/tools'}}}}},
            'shared_invocation': {'on': {'backend_operation': {'to': 'shared_invocation_response',
                                                               'expect': {'kind': 'effect',
                                                                          'target': 'C91.shared_api',
                                                                          'outcome': 'invoke',
                                                                          'detail': {'endpoint': 'POST '
                                                                                                 '/tools'}}}}},
            'direct_catalog': {'on': {'backend_operation': {'to': 'direct_catalog_response',
                                                            'expect': {'kind': 'effect',
                                                                       'target': 'bound_backend_client',
                                                                       'outcome': 'catalog',
                                                                       'detail': {'endpoint': 'GET '
                                                                                              '/tools'}}}}},
            'direct_invocation': {'on': {'backend_operation': {'to': 'direct_invocation_response',
                                                               'expect': {'kind': 'effect',
                                                                          'target': 'bound_backend_client',
                                                                          'outcome': 'invoke',
                                                                          'detail': {'endpoint': 'POST '
                                                                                                 '/tools'}}}}},
            'shared_catalog_response': {'on': {'return_envelope': {'to': 'done',
                                                                   'expect': {'kind': 'output',
                                                                              'outcome': 'shared_catalog'}}}},
            'shared_invocation_response': {'on': {'return_envelope': {'to': 'done',
                                                                      'expect': {'kind': 'output',
                                                                                 'outcome': 'shared_invocation'}}}},
            'direct_catalog_response': {'on': {'return_envelope': {'to': 'done',
                                                                   'expect': {'kind': 'output',
                                                                              'outcome': 'direct_catalog'}}}},
            'direct_invocation_response': {'on': {'return_envelope': {'to': 'done',
                                                                      'expect': {'kind': 'output',
                                                                                 'outcome': 'direct_invocation'}}}},
            'done': {'type': 'final'}}},
)
```
