---
atom_family: SPEC
atom_id: AN-S-3286
container:
  component: C49
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3052
state:
  status: draft
  version: 4
  updated_at: '2026-11-25T12:00:00Z'
---

## Summary

Process Codex Hook events locally

## Guarantee

The Hook is installed in user-global Codex configuration and matches ANECHOIC MCP requests only. Given a Codex `PreToolUse` event on standard input, it returns one JSON response on standard output. It returns an empty response for other Tools.

For an ANECHOIC MCP request, resolve the event's absolute `cwd` through the local filesystem. Find the nearest canonical Git worktree root by walking upward to a `.git` directory or file marker. Bind that root and the event's session ID to the request.

Deny malformed or conflicting input, a missing worktree root, or an explicit Project root that does not match the resolved root. Deny a caller session ID that conflicts with the event's session ID.

The Hook makes no subprocess or other Component calls. It uses local filesystem access and host input and output.

## Claim

### Prose Claim

The trace claim covers the selected workflow's successful responses. It forbids subprocess and other Component calls. The trace targets `subprocess` and `component_call` denote those effects.

### Formal Claim

```python cli
declare_cli_contract(
    interface='pre_tool_use',
    runner='uv',
    path='<codex-home>/anechoic/codex_hook.py',
    arguments=('run', '--no-project', '--no-env-file', '--managed-python', '--python', '3.14', '<installed-hook>'),
    stdin='Codex PreToolUse event JSON on stdin',
    stdout='Codex hook result JSON on stdout',
    action='bind_codex_hook_request',
    output='succeeded',
    forbid_effect=('subprocess', 'component_call'),
)
```

The response content, root and session checks, and denied paths remain prose requirements.
