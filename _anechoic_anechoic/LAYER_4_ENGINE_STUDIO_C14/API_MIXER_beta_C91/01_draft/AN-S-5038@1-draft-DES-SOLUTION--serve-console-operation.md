---
atom_family: SPEC
atom_id: AN-S-5038
container:
  component: C91
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-4809@6-draft
state:
  status: draft
  version: 1
  updated_at: "2026-11-26T23:31:05Z"
---
## Summary

Serve a Console operation for its admitted Project

## Claim

### Prose Claim

Use C71 for the query projection and C68 for authored Atom reads, lifecycle effects, and rebuilds. Preserve the selected binding and separate Graph and full rebuild targets.

### Formal Claim

```python
component_workflow(component='C91', action='serve_console_operation',
                   machine={'id': 'c91_serve_console_operation',
 'initial': 'idle',
 'states': {'done': {'type': 'final'},
            'idle': {'on': {'requested': {'expect': {'kind': 'trigger'},
                                          'to': 'running'}}},
            'returning': {'on': {'succeeded': {'expect': {'kind': 'output',
                                                          'outcome': 'succeeded'},
                                               'to': 'done'}}},
            'running': {'on': {'completed': {'expect': {'kind': 'effect',
                                                        'outcome': 'console_operation_returned',
                                                        'target': 'C91.console'},
                                             'to': 'returning'},
                               'failed': {'expect': {'kind': 'output',
                                                     'outcome': 'failed'},
                                          'to': 'done'}}}}})
```

```python
component_workflow(component='C91', action='dispatch_console_document', machine={'id': 'c91_dispatch_console_document',
 'initial': 'idle',
 'states': {'current_1': {'on': {'current': {'expect': {'kind': 'output', 'outcome': 'current'},
                                             'to': 'done'}}},
            'done': {'type': 'final'},
            'exact_1': {'on': {'exact': {'expect': {'kind': 'output', 'outcome': 'exact'},
                                         'to': 'done'}}},
            'idle': {'on': {'requested': {'expect': {'kind': 'trigger'}, 'to': 'running'}}},
            'running': {'on': {'current_1': {'expect': {'detail': {'selector': 'current'},
                                                        'kind': 'effect',
                                                        'outcome': 'returned',
                                                        'target': 'C68.atom_document'},
                                             'to': 'current_1'},
                               'exact_1': {'expect': {'detail': {'selector': 'exact'},
                                                      'kind': 'effect',
                                                      'outcome': 'returned',
                                                      'target': 'C68.atom_document'},
                                           'to': 'exact_1'},
                               'failed': {'expect': {'kind': 'output', 'outcome': 'failed'},
                                          'to': 'done'}}}}})
```

```python
component_workflow(component='C91', action='dispatch_console_rebuild', machine={'id': 'c91_dispatch_console_rebuild',
 'initial': 'idle',
 'states': {'database_ready_1': {'on': {'database_ready': {'expect': {'kind': 'output',
                                                                      'outcome': 'database_ready'},
                                                           'to': 'done'}}},
            'done': {'type': 'final'},
            'graph_ready_1': {'on': {'graph_ready': {'expect': {'kind': 'output',
                                                                'outcome': 'graph_ready'},
                                                     'to': 'done'}}},
            'idle': {'on': {'requested': {'expect': {'kind': 'trigger'}, 'to': 'running'}}},
            'running': {'on': {'database_ready_1': {'expect': {'detail': {'scope': 'all'},
                                                               'kind': 'effect',
                                                               'outcome': 'admitted',
                                                               'target': 'C68.build'},
                                                    'to': 'database_ready_1'},
                               'failed': {'expect': {'kind': 'output', 'outcome': 'failed'},
                                          'to': 'done'},
                               'graph_ready_1': {'expect': {'detail': {'scope': 'realization_graph'},
                                                            'kind': 'effect',
                                                            'outcome': 'admitted',
                                                            'target': 'C68.build'},
                                                 'to': 'graph_ready_1'}}}}})
```

```python
component_workflow(component='C91', action='report_console_runtime_health', machine={'id': 'c91_report_console_runtime_health',
 'initial': 'idle',
 'states': {'done': {'type': 'final'},
            'healthy_1': {'on': {'healthy': {'expect': {'kind': 'output', 'outcome': 'healthy'},
                                             'to': 'done'}}},
            'idle': {'on': {'requested': {'expect': {'kind': 'trigger'}, 'to': 'running'}}},
            'running': {'on': {'healthy_1': {'expect': {'detail': {'state': 'ready'},
                                                        'kind': 'effect',
                                                        'outcome': 'reported',
                                                        'target': 'C91.console_status'},
                                             'to': 'healthy_1'},
                               'starting_1': {'expect': {'detail': {'state': 'pending'},
                                                         'kind': 'effect',
                                                         'outcome': 'reported',
                                                         'target': 'C91.console_status'},
                                              'to': 'starting_1'},
                               'unavailable_1': {'expect': {'detail': {'state': 'unavailable'},
                                                            'kind': 'effect',
                                                            'outcome': 'reported',
                                                            'target': 'C91.console_status'},
                                                 'to': 'unavailable_1'},
                               'unhealthy_1': {'expect': {'detail': {'state': 'degraded'},
                                                          'kind': 'effect',
                                                          'outcome': 'reported',
                                                          'target': 'C91.console_status'},
                                               'to': 'unhealthy_1'}}},
            'starting_1': {'on': {'starting': {'expect': {'kind': 'output',
                                                          'outcome': 'starting'},
                                               'to': 'done'}}},
            'unavailable_1': {'on': {'unavailable': {'expect': {'kind': 'output',
                                                                'outcome': 'unavailable'},
                                                     'to': 'done'}}},
            'unhealthy_1': {'on': {'unhealthy': {'expect': {'kind': 'output',
                                                            'outcome': 'unhealthy'},
                                                 'to': 'done'}}}}})
```
