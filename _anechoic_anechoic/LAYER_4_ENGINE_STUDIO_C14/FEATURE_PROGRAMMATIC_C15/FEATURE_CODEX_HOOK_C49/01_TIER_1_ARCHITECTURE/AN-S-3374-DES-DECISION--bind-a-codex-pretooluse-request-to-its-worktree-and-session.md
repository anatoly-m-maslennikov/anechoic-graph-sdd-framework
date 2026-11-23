---
atom_family: SPEC
atom_id: AN-S-3374
container:
  component: C49
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-3361@2
  - AN-S-3387@2
  IS_SOLUTION_FOR:
  - AN-S-3286@3
state:
  status: active
  version: 2
  updated_at: '2026-11-23T03:50:52.802684+00:00'
---

## Summary

Bind a Codex PreToolUse request to its worktree and session.

## Claim

### Prose Claim

The hook resolves the nearest Git worktree, checks input and session
consistency, and returns an allow, deny, or empty response.

### Formal Claim

```python
component_workflow(
    component='C49',
    action='bind_codex_hook_request',
    machine={
        'id': 'c49_bind_codex_hook_request',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'pre_tool_use_received': {'target': 'checking', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'trigger'}}},
            }},
            'checking': {'on': {
                'git_worktree_resolved': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C49', 'outcome': 'succeeded'}}},
                'event_denied': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
                'other_tool_ignored': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
            }},
            'responding': {'on': {
                'updated_input_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
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
