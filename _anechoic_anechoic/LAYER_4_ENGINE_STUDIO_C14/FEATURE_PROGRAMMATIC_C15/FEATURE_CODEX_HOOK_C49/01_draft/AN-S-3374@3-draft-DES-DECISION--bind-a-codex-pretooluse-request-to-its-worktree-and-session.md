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
  IS_SOLUTION_FOR:
  - AN-S-3286@4-draft
state:
  status: draft
  version: 3
  updated_at: '2026-11-25T12:00:00Z'
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
                    {'kind': 'trigger', 'target': 'pre_tool_use', 'detail': {
                        'transport': 'cli', 'runner': 'uv', 'path': '<codex-home>/anechoic/codex_hook.py',
                        'arguments': ['run', '--no-project', '--no-env-file', '--managed-python', '--python',
                                      '3.14', '<installed-hook>'],
                        'stdin': 'Codex PreToolUse event JSON on stdin'}}}},
            }},
            'checking': {'on': {
                'git_worktree_resolved': {'target': 'responding', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C49', 'outcome': 'succeeded'}}},
                'event_denied': {'target': 'reporting_denial', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'hook_request', 'outcome': 'denied'}}},
                'other_tool_ignored': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded', 'detail': {'stdout': 'Codex hook result JSON on stdout'}}}},
            }},
            'responding': {'on': {
                'updated_input_returned': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded', 'detail': {'stdout': 'Codex hook result JSON on stdout'}}}},
            }},
            'reporting_denial': {'on': {
                'denial_returned': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'stdout': 'Codex hook result JSON on stdout'}}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

## Details

This Solution defines the expected event sequence for the selected workflow.
Trace conformance requires recorded evidence. Record subprocess calls as
`subprocess` effects and other Component calls as `component_call` effects.
