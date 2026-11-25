---
atom_family: SPEC
atom_id: AN-S-3366
container:
  component: C21
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3191@5
state:
  status: active
  version: 3
  updated_at: '2026-11-23T03:50:52.802684+00:00'
---
## Summary

Forward an admitted MCP Tool call to the shared Backend

## Claim

### Prose Claim

MCP forwards the Tool name, arguments, and caller context to the selected
native or Beta Backend. It returns the Backend result or a failure.

### Formal Claim

```python
component_workflow(
    component='C21',
    action='mcp_forward_tool',
    machine={
        'id': 'c21_mcp_forward_tool',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'mcp_tool_call': {'target': 'forwarding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'forwarding': {'on': {
                'backend_call_completed': [
                    {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'target': 'C45', 'outcome': 'succeeded'}}},
                    {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                        {'kind': 'effect', 'target': 'C70', 'outcome': 'succeeded'}}},
                ],
                'tool_call_refused_or_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'responding': {'on': {
                'tool_result_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
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
