---
atom_family: SPEC
atom_id: AN-S-3383
container:
  component: C66
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3316@3-draft
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T10:45:23+00:00'
---

## Summary

Run and track one Manifest compiler Worker.

## Claim

### Prose Claim

Start and track one compiler run. Reap each started process before
recording its terminal status. A deadline or accepted stop kills the
process before reaping it. A deadline raises a timeout. This flow
covers a run with at most one termination trigger. A successful status
request returns the active runs and the latest terminal runs as a read-only
model. Response field names and behavior for missing or foreign bindings
remain open.

### Formal Claim

```python
component_workflow(
    component='C66',
    action='manifest_compiler_worker_run',
    machine={
        'id': 'c66_manifest_compiler_worker_run',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'worker_requested': {'target': 'starting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'compiler_worker', 'detail': {
                        'transport': 'in_process',
                        'entry': 'ORCHESTRATOR_C66__shared.Orchestrator.run_worker',
                    }}}},
            }},
            'starting': {'on': {
                'compiler_process_started': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'started', 'target': 'C66.worker_process'}}},
                'launch_failure_recorded': {'target': 'raise_launch_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'failed', 'target': 'C66'}}},
                'worker_request_rejected': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'running': {'on': {
                'compiler_process_reaped': {'target': 'record_normal_exit', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'reaped', 'target': 'C66.worker_process'}}},
                'worker_deadline_elapsed': {'target': 'kill_for_timeout', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
                'worker_stop_accepted': {'target': 'kill_for_stop', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'record_normal_exit': {'on': {
                'terminal_run_recorded': [
                    {'target': 'return_result', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'outcome': 'completed', 'target': 'C66.worker_run'}}},
                    {'target': 'report_failure', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'outcome': 'failed', 'target': 'C66.worker_run'}}},
                ],
            }},
            'kill_for_timeout': {'on': {
                'compiler_process_killed': {'target': 'reap_for_timeout', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'killed', 'target': 'C66.worker_process'}}},
            }},
            'reap_for_timeout': {'on': {
                'compiler_process_reaped': {'target': 'record_timeout', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'reaped', 'target': 'C66.worker_process'}}},
            }},
            'record_timeout': {'on': {
                'terminal_run_recorded': {'target': 'raise_timeout', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'timed_out', 'target': 'C66.worker_run'}}},
            }},
            'raise_timeout': {'on': {
                'worker_timeout_raised': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'timed_out'}}},
            }},
            'kill_for_stop': {'on': {
                'compiler_process_killed': {'target': 'reap_for_stop', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'killed', 'target': 'C66.worker_process'}}},
            }},
            'reap_for_stop': {'on': {
                'compiler_process_reaped': {'target': 'record_stop', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'reaped', 'target': 'C66.worker_process'}}},
            }},
            'record_stop': {'on': {
                'terminal_run_recorded': {'target': 'return_stopped_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'cancelled', 'target': 'C66.worker_run'}}},
            }},
            'return_stopped_result': {'on': {
                'compiler_result_returned': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'raise_launch_error': {'on': {
                'worker_error_raised': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'return_result': {'on': {
                'compiler_result_returned': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'completed'}}},
            }},
            'report_failure': {'on': {
                'compiler_result_returned': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
                'worker_error_raised': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```


```python
component_workflow(
    component='C66',
    action='manifest_compiler_worker_status',
    machine={
        'id': 'c66_manifest_compiler_worker_status',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'status_requested': {'target': 'returning', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger', 'target': 'worker_runs', 'detail': {
                        'transport': 'http', 'route': 'GET /jobs/worker-runs',
                        'operation': 'worker_runs',
                    }}}},
            }},
            'returning': {'on': {
                'active_runs_returned': {'target': 'await_terminal_runs', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'returned', 'target': 'C66.active_runs'}}},
                'terminal_runs_returned': {'target': 'await_active_runs', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'returned', 'target': 'C66.latest_terminal_runs'}}},
            }},
            'await_terminal_runs': {'on': {
                'terminal_runs_returned': {'target': 'return_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'returned', 'target': 'C66.latest_terminal_runs'}}},
            }},
            'await_active_runs': {'on': {
                'active_runs_returned': {'target': 'return_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'returned', 'target': 'C66.active_runs'}}},
            }},
            'return_result': {'on': {
                'status_returned': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
