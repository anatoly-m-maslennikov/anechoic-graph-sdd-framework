---
atom_family: SPEC
atom_id: AN-S-3372
container:
  component: C46
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3306@3-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:59:12.784684+00:00'
---

## Summary

Run the current View in the browser

## Claim

### Prose Claim

In a ready Workspace, synchronize a dirty View before Run. Fetch the
first page using the completed Run's query ID. Report a missing query ID,
a failed Run, or a transport error. For a partial save, show the save
error, fetch and display the completed result, and finish with partial outcome.

### Formal Claim

```python
component_workflow(
    component='C46',
    action='workbench_frontend_run_view',
    machine={
        'id': 'c46_workbench_frontend_run_view',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'run_selected': [
                    {'target': 'syncing', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'trigger', 'detail': {'view_dirty': True}}}},
                    {'target': 'dispatching', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'trigger', 'detail': {'view_dirty': False}}}},
                ],
            }},
            'syncing': {'on': {
                'view_update_reply': {'target': 'dispatching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_update', 'outcome': 'succeeded'}}},
                'sync_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'dispatching': {'on': {
                'run_dispatched': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21', 'detail': {
                        'interface': 'workbench_http', 'transport': 'http',
                        'route': 'POST /anechoic/{project_name}/api/view_run', 'operation': 'view_run'}}}},
            }},
            'running': {'on': {
                'run_reply_failed': {'target': 'reporting_run_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.error', 'outcome': 'returned',
                     'detail': {'component': 'C21', 'action': 'workbench_view_run', 'output': 'failed'}}}},
                'run_reply_with_query_id': {'target': 'fetching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.query_id', 'outcome': 'returned',
                     'bind': {'run_query_id': 'query_id'},
                     'detail': {'component': 'C21', 'action': 'workbench_view_run',
                                'output': 'succeeded', 'has_query_id': True}}}},
                'run_reply_partial_with_query_id': {'target': 'partial_save_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.query_id', 'outcome': 'returned',
                     'bind': {'run_query_id': 'query_id'},
                     'detail': {'component': 'C21', 'action': 'workbench_view_run', 'output': 'partial'}}}},
                'run_reply_missing_query_id': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.malformed_reply', 'outcome': 'missing_query_id',
                     'detail': {'has_query_id': False}}}},
                'run_request_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'partial_save_error': {'on': {
                'run_reply_partial_save_error': {'target': 'showing_save_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.save_error', 'outcome': 'returned',
                     'detail': {'component': 'C21', 'action': 'workbench_view_run', 'output': 'partial'}}}},
                'partial_reply_malformed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.malformed_reply'}}},
                'partial_reply_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'showing_save_error': {'on': {
                'save_error_displayed': {'target': 'partial_fetching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_save_error', 'outcome': 'shown'}}},
                'save_error_display_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'partial_fetching': {'on': {
                'partial_first_page_received': {'target': 'partial_displaying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_fetch', 'outcome': 'succeeded',
                     'same_as': {'query_id': 'run_query_id'}}}},
                'partial_fetch_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'partial_displaying': {'on': {
                'partial_result_displayed': {'target': 'partial_finishing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_display', 'outcome': 'shown'}}},
                'partial_display_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'partial_finishing': {'on': {
                'run_partial': {'target': 'partial', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'partial'}}},
            }},
            'fetching': {'on': {
                'first_page_received': {'target': 'displaying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_fetch', 'outcome': 'succeeded',
                     'same_as': {'query_id': 'run_query_id'}}}},
                'fetch_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run', 'outcome': 'failed'}}},
            }},
            'displaying': {'on': {
                'result_displayed': {'target': 'finishing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_display', 'outcome': 'shown'}}},
            }},
            'finishing': {'on': {
                'run_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'reporting_run_error': {'on': {
                'run_error_displayed': {'target': 'finishing_run_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run_error', 'outcome': 'shown'}}},
            }},
            'finishing_run_failure': {'on': {
                'run_failure_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'run_failed'}}},
            }},
            'reporting_error': {'on': {
                'query_error_displayed': {'target': 'finishing_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_run_error', 'outcome': 'shown'}}},
            }},
            'finishing_failure': {'on': {
                'failure_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'partial': {'type': 'final'},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C46',
    action='workbench_frontend_check_view',
    machine={
        'id': 'c46_check_view',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'check_selected': {'target': 'waiting', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'view_check',
                    },
                }},
            }},
            'waiting': {'on': {
                'check_reply_current': {'target': 'showing_verdict', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'project_api.view_check', 'outcome': 'returned',
                        'detail': {
                            'sql': 'current',
                        },
                    },
                }},
                'check_reply_failed': {'target': 'clearing_verdict', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'project_api.view_check', 'outcome': 'failed',
                    },
                }},
            }},
            'showing_verdict': {'on': {
                'verdict_displayed': {'target': 'retaining_result', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'workbench_check_verdict', 'outcome': 'shown_for_current_sql',
                    },
                }},
            }},
            'retaining_result': {'on': {
                'result_preserved': {'target': 'reporting_check', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'workbench_previous_run', 'outcome': 'preserved',
                    },
                }},
            }},
            'reporting_check': {'on': {
                'finish': {'target': 'finished', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'checked',
                    },
                }},
            }},
            'clearing_verdict': {'on': {
                'verdict_cleared': {'target': 'showing_error', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'workbench_prior_check_verdict', 'outcome': 'cleared',
                    },
                }},
            }},
            'showing_error': {'on': {
                'error_displayed': {'target': 'retaining_failed_result', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'workbench_check_error', 'outcome': 'shown',
                    },
                }},
            }},
            'retaining_failed_result': {'on': {
                'result_preserved': {'target': 'reporting_failure', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'workbench_previous_run', 'outcome': 'preserved',
                    },
                }},
            }},
            'reporting_failure': {'on': {
                'finish': {'target': 'finished', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'failed',
                    },
                }},
            }},
            'finished': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C46',
    action='workbench_frontend_edit_sql',
    machine={
        'id': 'c46_edit_sql',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'sql_changed': {'target': 'clearing_verdict', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'editor_sql',
                    },
                }},
            }},
            'clearing_verdict': {'on': {
                'verdict_cleared': {'target': 'retaining_result', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'workbench_prior_check_verdict', 'outcome': 'cleared',
                    },
                }},
            }},
            'retaining_result': {'on': {
                'result_preserved': {'target': 'reporting_change', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'workbench_previous_run', 'outcome': 'preserved',
                    },
                }},
            }},
            'reporting_change': {'on': {
                'finish': {'target': 'finished', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'changed',
                    },
                }},
            }},
            'finished': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
