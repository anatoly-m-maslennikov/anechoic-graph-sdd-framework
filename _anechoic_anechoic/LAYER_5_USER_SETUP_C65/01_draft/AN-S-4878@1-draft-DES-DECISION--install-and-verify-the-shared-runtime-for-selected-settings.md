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
the user-scope hook. Record a failure report when installation fails.

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
                'settings_validated': {'target': 'requesting_image', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65', 'outcome': 'settings_validated'}}},
                'invalid_settings': {'target': 'reporting_invalid_settings', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65.install_failure', 'outcome': 'reported'}}},
            }},
            'requesting_image': {'on': {
                'release_build_image_requested': {'target': 'building', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C27', 'outcome': 'build_image_requested',
                        'detail': {
                            'interface': 'release', 'transport': 'cli', 'runner': 'uv',
                            'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                            'command': 'build-image',
                        },
                    },
                }},
            }},
            'building': {'on': {
                'image_built': {'target': 'requesting_launch', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'image_built'}}},
                'build_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65.install_failure', 'outcome': 'reported'}}},
            }},
            'requesting_launch': {'on': {
                'release_run_image_requested': {'target': 'starting', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C27', 'outcome': 'run_image_requested',
                        'detail': {
                            'interface': 'release', 'transport': 'cli', 'runner': 'uv',
                            'path': 'LAYER_3_DEVOPS_C80/LAYER_2_RELEASE_C27/release.py',
                            'command': 'run-image',
                            'apply': True, 'verify_mcp': True,
                        },
                    },
                }},
            }},
            'starting': {'on': {
                'runtime_started': {'target': 'verifying_mcp', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'runtime_started'}}},
                'start_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65.install_failure', 'outcome': 'reported'}}},
            }},
            'verifying_mcp': {'on': {
                'mcp_verified_single_project': {'target': 'verifying_project', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'shared_runtime_mcp', 'outcome': 'verified',
                     'detail': {'setup_mode': 'single_project', 'component': 'C81',
                                'action': 'apply_shared_runtime_launch', 'output': 'mcp_verified'}}}},
                'mcp_verified_projects_root': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'shared_runtime_mcp', 'outcome': 'verified',
                     'detail': {'setup_mode': 'projects_root', 'component': 'C81',
                                'action': 'apply_shared_runtime_launch', 'output': 'mcp_verified'}}}},
                'mcp_verification_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65.install_failure', 'outcome': 'reported'}}},
            }},
            'verifying_project': {'on': {
                'project_access_verified': {'target': 'reporting', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C27', 'outcome': 'project_access_verified'}}},
                'project_verification_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65.install_failure', 'outcome': 'reported'}}},
            }},
            'reporting': {'on': {
                'install_succeeded': {'target': 'succeeded', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'succeeded'}}},
                'install_failed': {'target': 'reporting_failure', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'effect', 'target': 'C65.install_failure', 'outcome': 'reported'}}},
            }},
            'reporting_invalid_settings': {'on': {
                'invalid_settings_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed', 'detail': {'reason': 'invalid_settings'}}}},
            }},
            'reporting_failure': {'on': {
                'failure_reported': {'target': 'failed', 'guard': {'type': 'matchesTrace', 'params':
                    {'kind': 'output', 'outcome': 'failed'}}},
            }},
            'succeeded': {'type': 'final'},
            'failed': {'type': 'final'},
        },
    },
)
```

```python
component_workflow(
    component='C65',
    action='prepare_setup_install',
    machine={
        'id': 'c65_setup_preparation',
        'initial': 'idle',
        'states': {
            'idle': {'on': {
                'prepare_install': {'target': 'checking_settings', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'trigger',
                    },
                }},
            }},
            'checking_settings': {'on': {
                'existing_settings_conflict': {'target': 'reporting_conflict', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C65.settings_options', 'outcome': 'conflict',
                    },
                }},
                'settings_consistent': {'target': 'selecting_initialization', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C65.settings_options', 'outcome': 'consistent',
                    },
                }},
            }},
            'selecting_initialization': {'on': {
                'single_project_init_requested': {'target': 'initializing_project', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C65.project_init_request', 'outcome': 'explicit_single_project',
                    },
                }},
                'no_init_requested': {'target': 'reporting_no_init', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C65.project_init_request', 'outcome': 'absent',
                    },
                }},
            }},
            'initializing_project': {'on': {
                'project_inputs_initialized': {'target': 'reporting_init', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'effect', 'target': 'C65.project_inputs', 'outcome': 'initialized',
                    },
                }},
            }},
            'reporting_conflict': {'on': {
                'conflict_reported': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'conflicting_settings_preserved',
                    },
                }},
            }},
            'reporting_init': {'on': {
                'explicit_init_reported': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'explicit_project_initialized',
                    },
                }},
            }},
            'reporting_no_init': {'on': {
                'inputs_preserved': {'target': 'done', 'guard': {
                    'type': 'matchesTrace', 'params': {
                        'kind': 'output', 'outcome': 'project_inputs_preserved',
                    },
                }},
            }},
            'done': {'type': 'final'},
        },
    },
)
```
