---
atom_family: SPEC
atom_id: AN-S-3052
container:
  component: C15
tier: 4
context:
  template: component_manifest
  lens: SPEC
state:
  status: active
  version: 5
  updated_at: '2026-11-22T11:23:40.206159+00:00'
---

## Summary

Declare CODEX_HOOK

## Formal manifest

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ComponentManifest

declare_entity(
    entity_name='Component Manifest',
    instance=ComponentManifest(
        component_id='C49',
        name='CODEX_HOOK',
        lens_whitelist=['DES'],
        boundaries={
            'code': {
                'imports': {'only': []},
                'exports': {
                    'FEATURE_CODEX_HOOK__shared': None,
                    'FEATURE_CODEX_HOOK__shared.main': None,
                },
            },
            'io': {
                'server': {
                    'pre_tool_use': {
                        'transport': 'cli',
                        'runner': 'uv',
                        'path': '<codex-home>/anechoic/codex_hook.py',
                        'arguments': ['run', '--no-project', '--no-env-file', '--managed-python', '--python', '3.14', '<installed-hook>'],
                        'input': 'Codex PreToolUse event JSON on stdin',
                        'output': 'Codex hook result JSON on stdout',
                    },
                },
                'client': [],
            },
            'state': {
                'reads': ['Git worktree marker for the event working directory'],
                'writes': [],
            },
        },
    ),
)
```
