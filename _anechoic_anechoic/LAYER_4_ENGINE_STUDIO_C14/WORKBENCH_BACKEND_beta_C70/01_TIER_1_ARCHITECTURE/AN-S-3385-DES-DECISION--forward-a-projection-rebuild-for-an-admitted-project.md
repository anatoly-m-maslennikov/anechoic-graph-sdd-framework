---
atom_family: SPEC
atom_id: AN-S-3385
container:
  component: C70
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3340@27
state:
  status: active
  version: 3
  updated_at: '2026-11-23T03:50:52.802684+00:00'
---
## Summary

Forward a projection rebuild for an admitted Project.

## Claim

### Prose Claim

For an `all` or projection table target, the Backend validates the target,
asks the Project Orchestrator to build, and returns replacement result IDs.
For result and flow-history targets, it forwards the rebuild to Kernel.

### Formal Claim

```python
component_workflow(
    component='C70',
    action='beta_backend_rebuild_projection',
    machine={
        'id': 'c70_beta_backend_rebuild_projection',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'rebuild_requested': {'target': 'step_1', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'step_1': {'on': {
                'validate_target_and_forward_build': {'target': 'step_2', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C68'}}},
            }},
            'step_2': {'on': {
                'return_replacement_ids': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

## Details

The Formal Claim covers the Orchestrator path only. Its event names describe
an expected sequence; the Backend does not record them as flow events.
Trace conformance requires recorded evidence.
