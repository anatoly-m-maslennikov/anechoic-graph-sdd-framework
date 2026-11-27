---
atom_family: SPEC
atom_id: AN-S-5070
container:
  component: C49
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3052@9-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Bind a Codex PreToolUse request to its worktree and session.

## Claim

### Prose Claim

Decode the bounded event input and inspect the Tool name. For another
Tool, emit the empty JSON object. Otherwise resolve the canonical
worktree and check the Tool arguments and session against the event.

On success, copy the Tool arguments and caller context. Set only
`project_root` and `caller_context.session_id` to the resolved root
and the original event session. Include the copy in `updatedInput`.
On refusal, return a JSON denial and omit `updatedInput`.

For the value check, read the resolved root and supplied values from
the worktree and event. Read the corresponding values and denial
reason from the response. Record `forwarded_input` if the response
contains the `updatedInput` field, even if that field is empty.

Write one JSON value and exit with status zero on each response path.
The interpreter performs the checks and binding locally.

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
                'pre_tool_use_received': {'target': 'checking',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'trigger', 'target': 'pre_tool_use',
                        'detail': {
                            'transport': 'cli',
                            'runner': 'uv',
                            'path': '<codex-home>/anechoic/codex_hook.py',
                            'arguments': ['run', '--no-project', '--no-env-file', '--managed-python',
                                          '--python', '3.14', '<installed-hook>'],
                            'stdin': 'Codex PreToolUse event JSON on stdin',
                        },
                    }}},
            }},
            'checking': {'on': {
                'worktree_and_session_bound': {'target': 'preparing_allow',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'hook_request', 'outcome': 'bound',
                    }}},
                'malformed_or_conflicting_input_refused': {'target': 'returning_denial',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'hook_request', 'outcome': 'denied',
                    }}},
                'other_tool_ignored': {'target': 'ignored',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'ignored',
                        'detail': {
                            'stdout': 'Codex hook result JSON on stdout',
                            'exit_code': 0,
                        },
                    }}},
            }},
            'preparing_allow': {'on': {
                'updated_input_included': {'to': 'returning_allow',
                    'expect': {
                        'kind': 'effect', 'target': 'forwarded_input',
                        'outcome': 'included',
                    }},
            }},
            'returning_allow': {'on': {
                'updated_input_returned': {'target': 'allowed',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'allowed',
                        'detail': {
                            'stdout': 'Codex hook result JSON on stdout',
                            'exit_code': 0,
                        },
                    }}},
            }},
            'returning_denial': {'on': {
                'denial_returned': {'target': 'denied',
                    'guard': {'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'denied',
                        'detail': {
                            'stdout': 'Codex hook result JSON on stdout',
                            'exit_code': 0,
                        },
                    }}},
            }},
            'allowed': {'type': 'final'},
            'denied': {'type': 'final'},
            'ignored': {'type': 'final'},
        },
    },
)
```
