---
atom_family: SPEC
atom_id: AN-S-3379
container:
  component: C62
tier: 1
context:
  template: DECISION
  lens: SPEC
relations:
  IS_SOLUTION_FOR:
  - AN-S-3186@4
state:
  status: archived
  version: 2
  updated_at: "2026-11-27T15:50:51.353081+00:00"
---

## Summary

Build and host the initial Model and Structure for a selected Project.

## Claim

### Prose Claim

Manifest Runtime requests a build, opens the admitted Model, publishes its
matching Structure, and yields both to its caller.

### Formal Claim

```python
component_workflow(
    component='C62',
    action='manifest_runtime_start',
    machine={
        'id': 'c62_manifest_runtime_start',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'runtime_opened': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'step_1': {'on': {
                'request_model_build': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C66'}}},
            }},
            'step_2': {'on': {
                'verify_model_and_publish_structure': {'target': 'step_3', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C62'}}},
            }},
            'step_3': {'on': {
                'yield_admitted_artifacts': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
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
