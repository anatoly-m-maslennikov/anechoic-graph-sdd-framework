---
atom_family: SPEC
atom_id: AN-S-3296
container:
  component: C00
tier: 1
context:
  template: component_manifest
  lens: SPEC
state:
  status: "active"
  version: 11
  updated_at: "2026-11-26T15:52:23.634458+00:00"
---

## Summary

Declare User Setup

## Purpose

Install and configure the machine-local shared ANECHOIC runtime for selected Projects. Keep runtime settings under User Setup ownership and initialize Project inputs only when requested.

## Component Identity

```python
from anechoic.model import ComponentManifest

ComponentManifest(
    component_id='C65',
    name='User Setup',
    layer=5,
    lens_whitelist=['DES', 'DevOps', 'QA', 'SWD'],
)
```

## Component Boundaries

```python
{'code': {'imports': {'only': ['C65']},
          'exports': {'RUNTIME_SETUP__shared.main': {'private': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.Settings': 'shared',
                      'RUNTIME_SETUP__shared.HOOK_SOURCE': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.MATCHER': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.install_codex': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.initialize_project': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.LAUNCHER': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.RELEASE': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.install': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.parse_arguments': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.select_settings': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']},
                      'RUNTIME_SETUP__shared.write_settings': {'shared': ['LAYER_5_USER_SETUP_C65/RUNTIME_SETUP__tests']}}},
 'io': {'server': {'runtime_setup': {'transport': 'cli',
                                     'runner': 'uv',
                                     'path': 'LAYER_5_USER_SETUP_C65/setup.py',
                                     'command': 'install'}},
        'client': [{'component': 'C27', 'interface': 'release'}]},
 'state': {'writes': ['Machine-local runtime.toml',
                      'Explicitly initialized Project inputs',
                      'Codex user config when selected']}}
```

## Component Contract

### Install the shared runtime

#### Guarantee

Run from the Framework checkout root:

```sh
setup="$PWD/LAYER_5_USER_SETUP_C65"
UV_PROJECT_ENVIRONMENT="$setup/.venv-setup" \
  uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/setup" \
    --locked --python 3.14 --managed-python --no-env-file \
    python -B -E "$setup/setup.py" install [--project PATH | --projects-root PATH] [--settings PATH] [--port PORT] [--workbench-storage disk|memory] [--journal-storage files|duckdb] [--init-project --name NAME --prefix PREFIX] [--agent codex]
```

A first installation selects one Project repository or a containing folder. Later runs may use the saved settings. Setup owns machine-local `runtime.toml`. New settings default to port 8092, disk Workbench storage, and file Journal storage. Existing settings must not be overwritten by conflicting options.

Use the machine-wide `[logging]` level in `runtime.toml` with default
`INFO`. Validate and pass it to Studio at startup under AN-S-4741.

Setup calls Release through its CLI to build an immutable shared runtime image and start it. Release verifies MCP through the published host port. For a single Project, it also verifies Project access. Only explicit `--init-project` initializes a new single Project.

`--agent codex` (or `--codex`) registers MCP and installs the user-scope `PreToolUse` hook. The hook selects the active Git worktree for each request. The user must trust the hook in Codex.

#### References

AN-S-3296 and AN-S-3310.
