---
atom_family: SPEC
atom_id: AN-S-3052
container:
  component: C15
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 8
  updated_at: "2026-11-26T15:52:28.814180+00:00"
---

## Summary

Declare CODEX_HOOK

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C49',
    name='CODEX_HOOK',
    lens_whitelist=['DES'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': []},
          'exports': {'FEATURE_CODEX_HOOK__shared': None,
                      'FEATURE_CODEX_HOOK__shared.main': None}},
 'io': {'server': {'pre_tool_use': {'transport': 'cli',
                                    'runner': 'uv',
                                    'path': '<codex-home>/anechoic/codex_hook.py',
                                    'arguments': ['run',
                                                  '--no-project',
                                                  '--no-env-file',
                                                  '--managed-python',
                                                  '--python',
                                                  '3.14',
                                                  '<installed-hook>'],
                                    'input': 'Codex PreToolUse event JSON '
                                             'on stdin',
                                    'output': 'Codex hook result JSON on '
                                              'stdout'}},
        'client': []},
 'state': {'reads': ['Git worktree marker for the event working '
                     'directory'],
           'writes': []}}
```

## Component Contract

### Process Codex Hook events locally

#### Guarantee

The Hook is installed in user-global Codex configuration and matches ANECHOIC MCP requests only. Given a Codex `PreToolUse` event on standard input, it returns one JSON response on standard output. It returns an empty response for other Tools.

For an ANECHOIC MCP request, resolve the event's absolute `cwd` through the local filesystem. Find the nearest canonical Git worktree root by walking upward to a `.git` directory or file marker. Bind that root and the event's session ID to the request.

Deny malformed or conflicting input, a missing worktree root, or an explicit Project root that does not match the resolved root. Deny a caller session ID that conflicts with the event's session ID.

The Hook makes no subprocess or other Component calls. It uses local filesystem access and host input and output.

#### References

AN-S-2621, AN-S-3052, and AN-T-2944.
