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
                'sync_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'dispatching': {'on': {
                'run_dispatched': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21', 'detail': {
                        'interface': 'workbench_http', 'transport': 'http',
                        'route': 'POST /anechoic/{project_name}/api/view_run', 'operation': 'view_run'}}}},
            }},
            'running': {'on': {
                'run_reply_failed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'failed'}}},
                'run_reply_with_query_id': {'target': 'fetching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.query_id', 'outcome': 'returned',
                     'detail': {'component': 'C21', 'action': 'workbench_view_run',
                                'output': 'succeeded', 'has_query_id': True}}}},
                'run_reply_partial_with_query_id': {'target': 'partial_save_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.query_id', 'outcome': 'returned',
                     'detail': {'component': 'C21', 'action': 'workbench_view_run', 'output': 'partial'}}}},
                'run_reply_missing_query_id': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.malformed_reply', 'outcome': 'missing_query_id',
                     'detail': {'has_query_id': False}}}},
                'run_request_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'partial_save_error': {'on': {
                'run_reply_partial_save_error': {'target': 'showing_save_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.save_error', 'outcome': 'returned',
                     'detail': {'component': 'C21', 'action': 'workbench_view_run', 'output': 'partial'}}}},
                'partial_reply_malformed': {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_run.malformed_reply'}}},
                'partial_reply_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'showing_save_error': {'on': {
                'save_error_displayed': {'target': 'partial_fetching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_save_error', 'outcome': 'shown'}}},
                'save_error_display_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'partial_fetching': {'on': {
                'partial_first_page_received': {'target': 'partial_displaying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_fetch', 'outcome': 'succeeded'}}},
                'partial_fetch_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'partial_displaying': {'on': {
                'partial_result_displayed': {'target': 'partial_finishing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_display', 'outcome': 'shown'}}},
                'partial_display_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'partial_finishing': {'on': {
                'run_partial': {'target': 'partial', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'partial'}}},
            }},
            'fetching': {'on': {
                'first_page_received': {'target': 'displaying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C21.view_fetch', 'outcome': 'succeeded'}}},
                'fetch_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'displaying': {'on': {
                'result_displayed': {'target': 'finishing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'workbench_display', 'outcome': 'shown'}}},
            }},
            'finishing': {'on': {
                'run_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'reporting_error': {'on': {
                'query_error_displayed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'partial': {'type': 'final'},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
