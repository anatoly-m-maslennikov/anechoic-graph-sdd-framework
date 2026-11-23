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
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@2
  IS_SOLUTION_FOR:
  - AN-S-3316@2
state:
  status: active
  version: 3
  updated_at: '2026-11-23T03:50:52.802684+00:00'
---

## Summary

Run and track one Manifest compiler Worker.

## Claim

### Prose Claim

Start and track one compiler run. Record completion or failure before
returning the result. A deadline or accepted stop kills the process
before recording its terminal status. A deadline raises a timeout.
This flow covers a run with at most one termination trigger.

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
                    {'kind': 'trigger'}}},
            }},
            'starting': {'on': {
                'compiler_process_started': {'target': 'running', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'succeeded', 'target': 'C50'}}},
                'launch_failure_recorded': {'target': 'raise_launch_error', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'failed', 'target': 'C66'}}},
                'worker_request_rejected': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'running': {'on': {
                'terminal_run_recorded': [
                    {'target': 'return_result', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'outcome': 'completed', 'target': 'C66'}}},
                    {'target': 'report_failure', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'outcome': 'failed', 'target': 'C66'}}},
                ],
                'worker_deadline_elapsed': {'target': 'kill_for_timeout', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
                'worker_stop_accepted': {'target': 'kill_for_stop', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'kill_for_timeout': {'on': {
                'compiler_process_killed': {'target': 'record_timeout', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'succeeded', 'target': 'C50'}}},
            }},
            'record_timeout': {'on': {
                'terminal_run_recorded': {'target': 'raise_timeout', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'timed_out', 'target': 'C66'}}},
            }},
            'raise_timeout': {'on': {
                'worker_timeout_raised': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'timed_out'}}},
            }},
            'kill_for_stop': {'on': {
                'compiler_process_killed': {'target': 'record_stop', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'succeeded', 'target': 'C50'}}},
            }},
            'record_stop': {'on': {
                'terminal_run_recorded': {'target': 'return_stopped_result', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'cancelled', 'target': 'C66'}}},
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

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
