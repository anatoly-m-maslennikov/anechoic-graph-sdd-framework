---
atom_family: SPEC
atom_id: AN-S-4798
container:
  component: C67
tier: 1
context:
  template: DECISION
  lens: SPEC
relations:
  IS_SOLUTION_FOR:
  - AN-S-4797@1
state:
  status: "active"
  version: 1
  updated_at: "2026-11-26T16:43:14.683091+00:00"
---
## Summary

Serve an accepted Beta artifact.

## Claim

### Prose Claim

For a successful Model or Structure request, the Database Server checks the
Project instance. The selected Host reads the artifact and generation ID
under the same lock. The Server returns the bytes and generation ID together.

### Formal Claim

```python
component_workflow(
    component='C67',
    action='beta_artifact_read',
    machine={
        'id': 'c67_beta_artifact_read',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'artifact_requested': {'target': 'reading', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'reading': {'on': {
                'accepted_artifact_read': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C71'}}},
            }},
            'responding': {'on': {
                'artifact_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'succeeded': {'type': 'final'},
        },
    },
)
```

## Details

This Solution models the successful read sequence. Trace conformance requires
recorded evidence; rejection and pre-admission outcomes are outside this model.
