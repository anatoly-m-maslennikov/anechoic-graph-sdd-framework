---
atom_family: SPEC
atom_id: AN-S-3316
container:
  component: C66
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3315
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T10:45:23+00:00'
---
## Summary

Track Manifest Compiler Worker runs

## Guarantee

For the admitted Project, start Model builds and Structure refreshes in
short-lived processes. Reap a process when it finishes or exceeds its
deadline. Report the active runs and the latest terminal run of each kind
through the declared Worker Run interface. Each record identifies the
run, its kind, the process if it started, and its status.

## Claim

### Prose Claim

For a failed run, record the failure. For a completed run, the trace records the process start and reap, and
the completed terminal run record. For a timed-out run, it records the
start, kill, and reap, and the timed-out terminal run record. Each
started process is reaped before its terminal run is recorded. A successful
status request returns the active runs and the latest terminal runs. The
response is read-only; its field names and behavior for missing or foreign
bindings remain open.

### Formal Claim

```python trace
declare_trace_contract(
    action='manifest_compiler_worker_run',
    interface='compiler_worker',
    transport='in_process',
    entry='ORCHESTRATOR_C66__shared.Orchestrator.run_worker',
    output='failed',
    must_effect=(('C66', 'failed'),),
)
```

```python trace
declare_trace_contract(
    action='manifest_compiler_worker_run',
    interface='compiler_worker',
    transport='in_process',
    entry='ORCHESTRATOR_C66__shared.Orchestrator.run_worker',
    output='completed',
    must_effect=(('C66.worker_process', 'started'),
                 ('C66.worker_process', 'reaped'),
                 ('C66.worker_run', 'completed')),
    must_precede=((('C66.worker_process', 'started'), ('C66.worker_process', 'reaped')),
                  (('C66.worker_process', 'reaped'), ('C66.worker_run', 'completed'))),
)
```


```python trace
declare_trace_contract(
    action='manifest_compiler_worker_run',
    interface='compiler_worker',
    transport='in_process',
    entry='ORCHESTRATOR_C66__shared.Orchestrator.run_worker',
    output='timed_out',
    must_effect=(('C66.worker_process', 'started'),
                 ('C66.worker_process', 'killed'),
                 ('C66.worker_process', 'reaped'),
                 ('C66.worker_run', 'timed_out')),
    must_precede=((('C66.worker_process', 'started'), ('C66.worker_process', 'killed')),
                  (('C66.worker_process', 'killed'), ('C66.worker_process', 'reaped')),
                  (('C66.worker_process', 'reaped'), ('C66.worker_run', 'timed_out'))),
)
```


```python trace
declare_trace_contract(
    action='manifest_compiler_worker_status',
    interface='worker_runs',
    route='GET /jobs/worker-runs',
    transport='http',
    operation='worker_runs',
    output='succeeded',
    must_effect=(('C66.active_runs', 'returned'),
                 ('C66.latest_terminal_runs', 'returned')),
    forbid_effect=('C66.worker_process', 'C66.worker_run'),
)
```
