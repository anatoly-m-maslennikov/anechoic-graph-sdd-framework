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
  - AN-S-3182@12-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T09:28:03.300533+00:00'
---

## Summary

Build a static Realization Graph snapshot

## Claim

### Prose Claim

Validate the Project request. Capture and resolve sources, then check
that the inputs stayed stable before returning the snapshot.

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
                    {'kind': 'trigger', 'target': 'build_graph', 'detail': {
                        'transport': 'cli', 'runner': 'managed_python',
                        'module': 'IWE_CONSOLE_C43.APP_IWE_CONSOLE.FEATURE_IMPORT_GRAPH_C61.realization_graph_cli',
                        'input_fields': ['root', 'config'],
                        'optional_paired_inputs': ['structure', 'control_root']}}}},
            }},
            'capturing': {'on': {
                'source_inventory_read': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'succeeded'}}},
                'graph_build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'graph_json_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded', 'detail': {
                        'encoding': 'json',
                        'output_fields': ['nodes', 'occurrences', 'edges', 'test_edges', 'read_issues',
                                          'state_effect_findings', 'code_access_findings']}}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```
