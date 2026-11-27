---
atom_family: SPEC
atom_id: AN-S-3373
container:
  component: C48
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3307@2
state:
  status: archived
  version: 2
  updated_at: "2026-11-27T15:50:51.353081+00:00"
---

## Summary

Read a Workbench MCP App resource

## Claim

### Prose Claim

A resource request selects the bundled compatibility or Workbench HTML and
returns it with the MCP App MIME type.

### Formal Claim

```python
component_workflow(
    component='C48',
    action='codex_extension_read_resource',
    machine={
        'id': 'c48_codex_extension_read_resource',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'resource_read_requested': {'target': 'reading', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'reading': {'on': {
                'html_loaded': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'outcome': 'succeeded'}}},
                'unknown_or_unavailable_resource': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'resource_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
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
