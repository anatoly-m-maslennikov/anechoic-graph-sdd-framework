---
atom_family: SPEC
atom_id: AN-S-3378
container:
  component: C61
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3182@11
state:
  status: archived
  version: 2
  updated_at: "2026-11-27T15:50:51.353081+00:00"
---

## Summary

Build a static Realization Graph snapshot

## Claim

### Prose Claim

The CLI validates a Project request, captures and resolves sources, checks
that inputs stayed stable, and emits graph rows as JSON.

### Formal Claim

```python
component_workflow(
    component='C61',
    action='import_graph_build_snapshot',
    machine={
        'id': 'c61_import_graph_build_snapshot',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'graph_build_requested': {'target': 'capturing', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'capturing': {'on': {
                'source_inventory_read': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'succeeded'}}},
                'graph_build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'graph_json_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
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
