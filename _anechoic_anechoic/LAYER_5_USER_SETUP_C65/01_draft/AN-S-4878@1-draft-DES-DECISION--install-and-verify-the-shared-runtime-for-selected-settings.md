---
atom_family: SPEC
atom_id: AN-S-4878
container:
  component: C65
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3297@9-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-25T00:00:00+00:00'
---

## Summary

Install and verify the shared runtime for selected settings.

## Claim

### Prose Claim

Only explicit `--init-project` initializes a new single Project. When
`--agent codex` or `--codex` is selected, Setup registers MCP and installs
the user-scope hook.

### Formal Claim

```python
component_workflow(
    component='C65',
    action='install_shared_runtime',
    machine={
        'id': 'c65_install_shared_runtime',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'install_requested': {'target': 'validating', 'guard': {'type': 'matchesTrace', 'params': {
                    'kind': 'trigger', 'target': 'runtime_setup', 'detail': {
                        'transport': 'cli', 'runner': 'uv', 'command': 'install',
                        'path': 'LAYER_5_USER_SETUP_C65/setup.py',
                    },
                }}},
            }},
            'validating': {'on': {
                'settings_validated': {'target': 'building', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65', 'outcome': 'settings_validated'}}},
                'invalid_settings': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'reason': 'invalid_settings'}}}},
            }},
            'building': {'on': {
                'image_built': {'target': 'starting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'image_built'}}},
                'build_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'starting': {'on': {
                'runtime_started': {'target': 'verifying_mcp', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'runtime_started'}}},
                'start_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'verifying_mcp': {'on': {
                'mcp_verified_single_project': {'target': 'verifying_project', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'mcp_verified', 'detail': {'setup_mode': 'single_project'}}}},
                'mcp_verified_projects_root': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'mcp_verified', 'detail': {'setup_mode': 'projects_root'}}}},
                'mcp_verification_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'verifying_project': {'on': {
                'project_access_verified': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'project_access_verified'}}},
                'project_verification_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'reporting': {'on': {
                'install_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'install_failed': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```
