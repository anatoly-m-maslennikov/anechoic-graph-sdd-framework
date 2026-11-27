---
atom_family: SPEC
atom_id: AN-S-5039
container:
  component: C68
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3337@30-draft
state:
  status: draft
  version: 1
  updated_at: "2026-11-26T23:31:05Z"
---
## Summary

Read and change exact Atom carriers and rebuild the selected Project scope

## Claim

### Prose Claim

Resolve the admitted carrier and validate its identity before returning its text. Apply Draft updates through lifecycle. Dispatch Graph-only and full generation captures separately.

Select relations by exact reference and include stable-ID links for
Current. Read editable Draft relations directly from the authored Header.

Use the Adapter's Model path classification to decide whether a lifecycle
operation requires a Project capture.

For a Current Ticket, pass the authored Header and the generation's
admitted Status domain to the lifecycle policy. Return its choices
with the Document.

### Formal Claim

```python
component_workflow(component='C68', action='run_console_source_operation',
                   machine={'id': 'c68_run_console_source_operation',
 'initial': 'idle',
 'states': {'done': {'type': 'final'},
            'idle': {'on': {'requested': {'expect': {'kind': 'trigger'},
                                          'to': 'running'}}},
            'returning': {'on': {'succeeded': {'expect': {'kind': 'output',
                                                          'outcome': 'succeeded'},
                                               'to': 'done'}}},
            'running': {'on': {'completed': {'expect': {'kind': 'effect',
                                                        'outcome': 'console_source_operation_completed',
                                                        'target': 'C68.console'},
                                             'to': 'returning'},
                               'failed': {'expect': {'kind': 'output',
                                                     'outcome': 'failed'},
                                          'to': 'done'}}}}})
```

```python
component_workflow(component='C68', action='read_console_atom_carrier', machine={'id': 'c68_read_console_atom_carrier',
 'initial': 'idle',
 'states': {'current_1': {'on': {'current_2': {'expect': {'detail': {'selector': 'current', 'incoming': 'selected_revision'},
                                                          'kind': 'effect',
                                                          'outcome': 'returned',
                                                          'target': 'C68.document'},
                                               'to': 'current_2'}}},
            'current_2': {'on': {'current': {'expect': {'kind': 'output', 'outcome': 'current'},
                                             'to': 'done'}}},
            'done': {'type': 'final'},
            'exact_1': {'on': {'exact_2': {'expect': {'detail': {'selector': 'exact', 'incoming': 'selected_revision'},
                                                      'kind': 'effect',
                                                      'outcome': 'returned',
                                                      'target': 'C68.document'},
                                           'to': 'exact_2'}}},
            'exact_2': {'on': {'exact': {'expect': {'kind': 'output', 'outcome': 'exact'},
                                         'to': 'done'}}},
            'idle': {'on': {'requested': {'expect': {'kind': 'trigger'}, 'to': 'running'}}},
            'running': {'on': {'current_1': {'expect': {'kind': 'effect',
                                                        'outcome': 'guarded_read',
                                                        'target': 'C68.carrier'},
                                             'to': 'current_1'},
                               'exact_1': {'expect': {'kind': 'effect',
                                                      'outcome': 'guarded_read',
                                                      'target': 'C68.carrier'},
                                           'to': 'exact_1'},
                               'failed': {'expect': {'kind': 'output', 'outcome': 'failed'},
                                          'to': 'done'}}}}})
```

```python
component_workflow(component='C68', action='rebuild_console_generation', machine={'id': 'c68_rebuild_console_generation',
 'initial': 'idle',
 'states': {'database_ready_1': {'on': {'database_ready_2': {'expect': {'kind': 'effect',
                                                                        'outcome': 'admitted',
                                                                        'target': 'C71.generation'},
                                                             'to': 'database_ready_2'}}},
            'database_ready_2': {'on': {'database_ready': {'expect': {'kind': 'output',
                                                                      'outcome': 'database_ready'},
                                                           'to': 'done'}}},
            'done': {'type': 'final'},
            'graph_ready_1': {'on': {'graph_ready_2': {'expect': {'kind': 'effect',
                                                                  'outcome': 'admitted',
                                                                  'target': 'C71.graph'},
                                                       'to': 'graph_ready_2'}}},
            'graph_ready_2': {'on': {'graph_ready': {'expect': {'kind': 'output',
                                                                'outcome': 'graph_ready'},
                                                     'to': 'done'}}},
            'idle': {'on': {'requested': {'expect': {'kind': 'trigger'}, 'to': 'running'}}},
            'running': {'on': {'database_ready_1': {'expect': {'kind': 'effect',
                                                               'outcome': 'captured',
                                                               'target': 'C69.source'},
                                                    'to': 'database_ready_1'},
                               'failed': {'expect': {'kind': 'output', 'outcome': 'failed'},
                                          'to': 'done'},
                               'graph_ready_1': {'expect': {'kind': 'effect',
                                                            'outcome': 'built',
                                                            'target': 'C69.graph'},
                                                 'to': 'graph_ready_1'}}}}})
```
