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
  - AN-S-3044@76
state:
  status: "active"
  version: 5
  updated_at: "2026-11-28T08:33:39.564167+00:00"
---

## Summary

Bridge the canonical Backend Tool REST operations

## Claim

### Prose Claim

The shared Console host and MCP use the C45 shared Tool coordinator for
catalog and invocation. The direct gateway serves its startup catalog and
uses the admitted Project client for calls. The legacy wrapper forwards
Tool names unchanged.

Check the shared Backend envelope and its Project receipt. Reject invalid
transport input before dispatch. Return a gateway fault if the shared
Backend reply fails validation.

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
                                                                     'outcome': 'transport_refused'}},
                            'legacy_interface': {'to': 'legacy_interface',
                                                 'expect': {'kind': 'trigger'}},
                            'invalid_legacy_request': {'to': 'done',
                                                       'expect': {'kind': 'output',
                                                                  'outcome': 'legacy_refused'}}}},
            'shared_catalog': {'on': {'backend_operation': {'to': 'shared_catalog_response',
                                                            'expect': {'kind': 'effect',
                                                                       'target': 'C45.shared_tool_coordinator',
                                                                       'outcome': 'catalog',
                                                                       'detail': {'endpoint': 'GET '
                                                                                              '/'}}}}},
            'shared_invocation': {'on': {'backend_operation': {'to': 'shared_invocation_response',
                                                               'expect': {'kind': 'effect',
                                                                          'target': 'C45.shared_tool_coordinator',
                                                                          'outcome': 'invoke',
                                                                          'detail': {'endpoint': 'POST '
                                                                                                 '/'}}}}},
            'direct_catalog': {'on': {'read_catalog_snapshot': {'to': 'direct_catalog_response',
                                                                'expect': {'kind': 'effect',
                                                                           'target': 'C21.backend_catalog_snapshot',
                                                                           'outcome': 'read',
                                                                           'detail': {}}}}},
            'direct_invocation': {'on': {'backend_operation': {'to': 'direct_invocation_response',
                                                               'expect': {'kind': 'effect',
                                                                          'target': 'bound_backend_client',
                                                                          'outcome': 'invoke',
                                                                          'detail': {'endpoint': 'POST '
                                                                                                 '/'}}}}},
            'shared_catalog_response': {'on': {'return_envelope': {'to': 'done',
                                                                   'expect': {'kind': 'output',
                                                                              'outcome': 'shared_catalog'}},
                                               'invalid_catalog': {'to': 'catalog_failed',
                                                                   'expect': {'kind': 'effect',
                                                                              'target': 'C21.tool_rest_reply',
                                                                              'outcome': 'refused',
                                                                              'detail': {'status': 503}}}}},
            'shared_invocation_response': {'on': {'return_envelope': {'to': 'done',
                                                                      'expect': {'kind': 'output',
                                                                                 'outcome': 'shared_invocation'}},
                                                  'invalid_receipt': {'to': 'receipt_failed',
                                                                      'expect': {'kind': 'effect',
                                                                                 'target': 'C21.tool_rest_reply',
                                                                                 'outcome': 'refused',
                                                                                 'detail': {'status': 502}}},
                                                  'invalid_reply': {'to': 'reply_failed',
                                                                    'expect': {'kind': 'effect',
                                                                               'target': 'C21.tool_rest_reply',
                                                                               'outcome': 'refused',
                                                                               'detail': {'status': 503}}}}},
            'direct_catalog_response': {'on': {'return_envelope': {'to': 'done',
                                                                   'expect': {'kind': 'output',
                                                                              'outcome': 'direct_catalog'}}}},
            'direct_invocation_response': {'on': {'return_envelope': {'to': 'done',
                                                                      'expect': {'kind': 'output',
                                                                                 'outcome': 'direct_invocation'}}}},
            'done': {'type': 'final'},
            'legacy_interface': {'on': {'legacy_dispatch': {'to': 'legacy_response',
                                                            'expect': {'kind': 'effect',
                                                                       'target': 'Backend.tool_dispatch',
                                                                       'outcome': 'invoke',
                                                                       'detail': {}}}}},
            'legacy_response': {'on': {'return_value_or_error': {'to': 'done',
                                                                 'expect': {'kind': 'output',
                                                                            'outcome': 'legacy_forwarded'}}}},
            'receipt_failed': {'on': {'return_fault': {'to': 'done',
                                                       'expect': {'kind': 'output',
                                                                  'outcome': 'shared_receipt_refused'}}}},
            'reply_failed': {'on': {'return_fault': {'to': 'done',
                                                     'expect': {'kind': 'output',
                                                                'outcome': 'shared_reply_invalid'}}}},
            'catalog_failed': {'on': {'return_fault': {'to': 'done',
                                                       'expect': {'kind': 'output',
                                                                  'outcome': 'shared_catalog_invalid'}}}}}},
)
```
