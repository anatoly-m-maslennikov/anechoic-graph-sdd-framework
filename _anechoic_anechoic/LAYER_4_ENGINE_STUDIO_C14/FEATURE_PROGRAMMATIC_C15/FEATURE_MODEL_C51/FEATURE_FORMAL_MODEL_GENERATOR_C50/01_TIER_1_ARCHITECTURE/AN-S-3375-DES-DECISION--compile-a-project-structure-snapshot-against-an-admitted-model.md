---
atom_family: SPEC
atom_id: AN-S-3375
container:
  component: C50
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3308@2
state:
  status: active
  version: 2
  updated_at: '2026-11-23T03:50:52.802684+00:00'
---

## Summary

Compile a Project Structure snapshot against an admitted Model.

## Claim

### Prose Claim

The compiler checks the Model descriptor and selected Manifest, compiles
the snapshot, and emits JSON; invalid or changed inputs are rejected.

### Formal Claim

```python
component_workflow(
    component='C50',
    action='compile_project_structure',
    machine={
        'id': 'c50_compile_project_structure',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'compilation_requested': {'target': 'admitting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'admitting': {'on': {
                'open_admitted_model_and_select_project': {'target': 'compiling', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C53'}}},
                'admission_or_selection_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'compiling': {'on': {
                'compile_structure_snapshot': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C50'}}},
                'invalid_or_changed_inputs': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'snapshot_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
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
