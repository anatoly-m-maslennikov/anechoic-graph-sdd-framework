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
  - AN-S-3306@2
state:
  status: "active"
  version: 2
  updated_at: "2026-11-26T16:43:14.639355+00:00"
---

## Summary

Run the current View in the browser

## Claim

### Prose Claim

In a ready Workspace, synchronize a dirty View before Run. Fetch the first
page if a successful Run supplies a query ID. Show a failed Run or
transport error.

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
                    {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'trigger', 'detail': {'view_dirty': False}}}},
                ],
            }},
            'syncing': {'on': {
                'view_update_reply': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'succeeded'}}},
                'sync_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'running': {'on': {
                'run_reply': [
                    {'target': 'fetching', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'outcome': 'succeeded', 'detail': {'has_query_id': True}}}},
                    {'target': 'displaying', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'outcome': 'succeeded', 'detail': {'has_query_id': False}}}},
                    {'target': 'reporting_error', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'outcome': 'failed'}}},
                ],
                'run_request_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'fetching': {'on': {
                'first_page_received': {'target': 'displaying', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'succeeded'}}},
                'fetch_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'displaying': {'on': {
                'result_displayed': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'reporting_error': {'on': {
                'query_error_displayed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
