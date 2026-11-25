---
atom_family: SPEC
atom_id: AN-S-3384
container:
  component: C69
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3336@25
state:
  status: active
  version: 2
  updated_at: '2026-11-23T03:50:52.802684+00:00'
---

## Summary

Build a pinned generation from an admitted Project binding.

## Claim

### Prose Claim

A Worker compiles the Model and Structure, captures the snapshot and graph,
then publishes sealed generation artifacts.

### Formal Claim

```python
component_workflow(
    component='C69',
    action='beta_worker_build_generation',
    machine={
        'id': 'c69_beta_worker_build_generation',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'generation_requested': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'step_1': {'on': {
                'compile_model_and_structure': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C69'}}},
            }},
            'step_2': {'on': {
                'build_graph_and_capture_snapshot': {'target': 'step_3', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C69'}}},
            }},
            'step_3': {'on': {
                'generation_artifacts_published': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C69', 'outcome': 'succeeded'}}},
            }},
            'responding': {'on': {
                'generation_receipt_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

## Details

The event names describe an expected sequence; the Worker does not record
them as flow events. Trace conformance requires recorded evidence.
