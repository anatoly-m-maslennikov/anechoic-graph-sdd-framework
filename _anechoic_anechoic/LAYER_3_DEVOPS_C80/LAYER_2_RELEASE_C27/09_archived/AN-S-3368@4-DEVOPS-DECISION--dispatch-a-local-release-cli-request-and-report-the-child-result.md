---
atom_family: SPEC
atom_id: AN-S-3368
concern:
  components:
  - C27
  - C63
container:
  component: C27
tier: 1
context:
  template: DECISION
  lens: DevOps
relations:
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@2
  IS_SOLUTION_FOR:
  - AN-S-3288@13
state:
  status: archived
  version: 4
  updated_at: '2026-11-23T14:32:18.783461+00:00'
---

## Summary

Dispatch a local release CLI request and report the child result.

## Claim

### Prose Claim

The release CLI dispatches the local command to C63, then reports its JSON
result and exit status.

### Formal Claim

```python
component_workflow(
    component='C27',
    action='dispatch_framework_release',
    machine={
        'id': 'c27_dispatch_framework_release',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'local_release_command_received': {'target': 'dispatching', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'dispatching': {'on': {
                'local_release_invoked': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C63'}}},
            }},
            'responding': {'on': {
                'release_json_reported': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output'}}},
            }},
            'reported': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence.
