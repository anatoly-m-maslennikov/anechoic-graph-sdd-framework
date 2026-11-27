---
atom_family: SPEC
atom_id: AN-S-3364
concern:
  subject: "Ticket"
  path: "Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom"
  relation: "is_narrower_than"
container:
  component: C16
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3304@2
state:
  status: active
  version: 6
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---

## Summary

Apply one admitted native Task or Ticket lifecycle request.

## Claim

### Prose Claim

The CLI checks the pinned Project and captures carriers before dispatch.
Apply the native lifecycle operation and result Contract in AN-S-3056.
A rejected request or runtime error can exit on stderr.

### Formal Claim

```python
component_workflow(
    component='C16',
    action='apply_native_lifecycle',
    machine={
        'id': 'c16_apply_native_lifecycle',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'lifecycle_request': {'target': 'checking', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'checking': {'on': {
                'pinned_carriers_captured': {'target': 'executing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C16', 'outcome': 'succeeded'}}},
                'request_rejected': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'executing': {'on': {
                'lifecycle_operation_dispatched': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C16'}}},
                'lifecycle_error': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'lifecycle_result': {'target': 'reported', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output'}}},
                'lifecycle_error': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'reported': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

Use AN-S-2686 for trace evidence.
