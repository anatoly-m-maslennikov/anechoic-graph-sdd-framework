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
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@1
  IS_SOLUTION_FOR:
  - AN-S-3340@24
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-23T01:48:06.208004+00:00"
---

## Summary

Forward a projection rebuild for an admitted Project.

## Claim

### Prose Claim

The Backend validates a projection target, asks the Project Orchestrator to
build, and returns replacement result IDs.

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

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
