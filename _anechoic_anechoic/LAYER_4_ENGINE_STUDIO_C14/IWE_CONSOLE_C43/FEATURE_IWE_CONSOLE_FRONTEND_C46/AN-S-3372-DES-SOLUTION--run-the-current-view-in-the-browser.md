---
atom_family: SPEC
atom_id: AN-S-3372
container:
  component: C46
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3060@15
state:
  status: "active"
  version: 8
  updated_at: "2026-11-27T20:33:22.444533+00:00"
---

## Summary

Run the current View in the browser

## Claim

### Formal Claim

```python
component_workflow(
    component='C46',
    action='workbench_frontend_run_view',
    machine={'id': 'c46_run_view',
 'initial': 'idle',
 'states': {'idle': {'on': {'run_selected': [{'to': 'syncing',
                                              'expect': {'kind': 'trigger',
                                                         'detail': {'view_dirty': True}}},
                                             {'to': 'acknowledging',
                                              'expect': {'kind': 'trigger',
                                                         'detail': {'view_dirty': False}}}]}},
            'syncing': {'on': {'view_update_reply': {'to': 'acknowledging',
                                                     'expect': {'kind': 'effect',
                                                                'target': 'C21.view_update',
                                                                'outcome': 'succeeded'}},
                               'sync_failed': {'to': 'done',
                                               'expect': {'kind': 'output',
                                                          'outcome': 'failed'}}}},
            'acknowledging': {'on': {'acknowledged_view': {'to': 'running',
                                                           'expect': {'kind': 'effect',
                                                                      'target': 'C46.acknowledged_view',
                                                                      'outcome': 'acknowledged'}}}},
            'running': {'on': {'run_reply': {'to': 'fetching',
                                             'expect': {'kind': 'effect',
                                                        'target': 'C21.view_run',
                                                        'outcome': 'returned'}},
                               'revision_error': {'to': 'revision_error',
                                                  'expect': {'kind': 'effect',
                                                             'target': 'C46.run_error',
                                                             'outcome': 'shown',
                                                             'detail': {'reason': 'revision'}}},
                               'missing_query_id_error': {'to': 'missing_query_id_error',
                                                          'expect': {'kind': 'effect',
                                                                     'target': 'C46.run_error',
                                                                     'outcome': 'shown',
                                                                     'detail': {'reason': 'query_id'}}},
                               'run_failed': {'to': 'done',
                                              'expect': {'kind': 'output',
                                                         'outcome': 'failed'}}}},
            'fetching': {'on': {'page_requested': {'to': 'reading',
                                                   'expect': {'kind': 'effect',
                                                              'target': 'C21.view_fetch',
                                                              'outcome': 'requested'}}}},
            'reading': {'on': {'first_page_received': {'to': 'displaying',
                                                       'expect': {'kind': 'effect',
                                                                  'target': 'C21.view_fetch',
                                                                  'outcome': 'returned'}},
                               'page_identity_error': {'to': 'page_error',
                                                       'expect': {'kind': 'effect',
                                                                  'target': 'C46.run_error',
                                                                  'outcome': 'shown',
                                                                  'detail': {'reason': 'page_identity'}}},
                               'fetch_failed': {'to': 'done',
                                                'expect': {'kind': 'output',
                                                           'outcome': 'failed'}}}},
            'displaying': {'on': {'result_displayed': {'to': 'returning',
                                                       'expect': {'kind': 'effect',
                                                                  'target': 'C46.result_display',
                                                                  'outcome': 'shown'}}}},
            'returning': {'on': {'return': {'to': 'done',
                                            'expect': {'kind': 'output',
                                                       'outcome': 'succeeded'}}}},
            'revision_error': {'on': {'return': {'to': 'done',
                                                 'expect': {'kind': 'output',
                                                            'outcome': 'revision_refused'}}}},
            'missing_query_id_error': {'on': {'return': {'to': 'done',
                                                         'expect': {'kind': 'output',
                                                                    'outcome': 'missing_query_id'}}}},
            'page_error': {'on': {'return': {'to': 'done',
                                             'expect': {'kind': 'output',
                                                        'outcome': 'page_refused'}}}},
            'done': {'type': 'final'}}},
)
```

```python
component_workflow(
    component='C46',
    action='workbench_frontend_call_tool',
    machine={'id': 'c46_tool_rest',
 'initial': 'idle',
 'states': {'idle': {'on': {'tool_requested': {'to': 'sending',
                                               'expect': {'kind': 'trigger'}},
                            'page_instance_invalid': {'to': 'done',
                                                      'expect': {'kind': 'output',
                                                                 'outcome': 'invalid_page_instance'}}}},
            'sending': {'on': {'rest_requested': {'to': 'waiting',
                                                  'expect': {'kind': 'effect',
                                                             'target': 'C21.tool_rest',
                                                             'outcome': 'requested',
                                                             'detail': {'endpoint': 'POST '
                                                                                    '/',
                                                                        'instance_header': 'X-Anechoic-Project-Instance'}}}}},
            'waiting': {'on': {'project_receipt': {'to': 'accepting',
                                                   'expect': {'kind': 'effect',
                                                              'target': 'C46.project_receipt',
                                                              'outcome': 'matched',
                                                              'detail': {}}},
                               'typed_refusal': {'to': 'refusing',
                                                 'expect': {'kind': 'effect',
                                                            'target': 'C46.typed_refusal',
                                                            'outcome': 'preserved',
                                                            'detail': {}}},
                               'project_receipt_mismatch': {'to': 'done',
                                                            'expect': {'kind': 'output',
                                                                       'outcome': 'receipt_refused'}},
                               'invalid_response': {'to': 'done',
                                                    'expect': {'kind': 'output',
                                                               'outcome': 'invalid_response'}}}},
            'accepting': {'on': {'return_value': {'to': 'done',
                                                  'expect': {'kind': 'output',
                                                             'outcome': 'succeeded'}}}},
            'refusing': {'on': {'return_refusal': {'to': 'done',
                                                   'expect': {'kind': 'output',
                                                              'outcome': 'refused'}}}},
            'done': {'type': 'final'}}},
)
```

## Semantics

Use the View revision acknowledged after synchronization.
The refusal events name the reported revision, receipt query ID, or
page identity error. Run and Run & Save use this same display path.
Preserve any result the Project already saved.
