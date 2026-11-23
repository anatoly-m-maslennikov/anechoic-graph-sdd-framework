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
  - AN-S-3387@1
  IS_SOLUTION_FOR:
  - AN-S-3316@2
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T23:52:17.262612+00:00'
---

## Summary

Run and track one Manifest compiler Worker.

## Claim

### Prose Claim

The Orchestrator starts a bounded compiler process, tracks the run and
records its terminal status.

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
                'worker_requested': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'step_1': {'on': {
                'start_compiler_process': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C50'}}},
            }},
            'step_2': {'on': {
                'record_terminal_worker_run': {'target': 'step_3', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66'}}},
            }},
            'step_3': {'on': {
                'return_compiler_result': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
