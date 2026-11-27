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
  status: draft
  version: 9
  updated_at: '2026-11-27T10:55:20+00:00'
---

## Summary

Declare CODEX_HOOK

## Purpose

Bind ANECHOIC MCP requests to the local Codex worktree and session.

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

The Hook runs from user-global Codex configuration and matches
ANECHOIC MCP requests. Given a Codex `PreToolUse` event on standard
input, return one JSON response on standard output. An event object
with a string name for another Tool returns the empty object.

Resolve an ANECHOIC request's absolute `cwd` through the local
filesystem. Walk upward from the canonical directory and use the
nearest worktree with a `.git` directory or regular-file marker.
Deny an unsafe marker or a missing worktree.

Deny malformed input, a missing session ID, an explicit Project root
that differs from the canonical root, or a caller session ID that
differs from the Codex session ID. On allow, bind the resolved root
and the Codex session ID in `updatedInput`. Preserve the other Tool
arguments and caller context.

The Hook uses host input and output and reads the local filesystem.
It calls neither subprocesses nor other Components and writes no
Project state.

#### Claim

An allowed response contains `permissionDecision: allow` and
`updatedInput` under `hookSpecificOutput`. A denied response contains
`permissionDecision: deny` and a nonempty `permissionDecisionReason`
in that object. The ignored response is `{}`.

Each response exits with process status zero. Codex reads the decision
from JSON.

The `worktree_and_session_bound` event observes the resolved root and
event session. It also observes the supplied Tool arguments without
`project_root` and `caller_context`, and the supplied caller context
without `session_id`. An absent caller context contributes an empty
object.

The `updated_input_returned` event observes the corresponding values
from the JSON response. The `forwarded_input` effect occurs exactly when
`hookSpecificOutput.updatedInput` is present. Refusal and ignore paths
forbid this effect. All paths forbid subprocess and other Component
calls.

The CLI Solution comparison checks exit codes and trace structure.
The equality and value type clauses require observations from the
execution of the Hook.

##### Formal Claim

```python cli
declare_cli_contract(
    interface='pre_tool_use',
    action='bind_codex_hook_request',
    stdin='Codex PreToolUse event JSON on stdin',
    stdout='Codex hook result JSON on stdout',
    exit_codes={'allowed': 0, 'denied': 0, 'ignored': 0},
    cases={
        'allowed': {
            'must_effect': (
                ('hook_request', 'bound'),
                ('forwarded_input', 'included'),
            ),
            'same_values': (
                (('worktree_and_session_bound', 'project_root'),
                 ('updated_input_returned', 'project_root')),
                (('worktree_and_session_bound', 'session_id'),
                 ('updated_input_returned', 'session_id')),
                (('worktree_and_session_bound', 'other_arguments'),
                 ('updated_input_returned', 'other_arguments')),
                (('worktree_and_session_bound', 'other_context'),
                 ('updated_input_returned', 'other_context')),
            ),
        },
        'denied': {
            'must_effect': (('hook_request', 'denied'),),
            'forbid_effect': ('forwarded_input',),
            'value_types': {('denial_returned', 'reason'): 'nonempty_string'},
        },
        'ignored': {'forbid_effect': ('hook_request', 'forwarded_input')},
    },
    invariant={'forbid_effect': ('subprocess', 'component_call')},
)
```
