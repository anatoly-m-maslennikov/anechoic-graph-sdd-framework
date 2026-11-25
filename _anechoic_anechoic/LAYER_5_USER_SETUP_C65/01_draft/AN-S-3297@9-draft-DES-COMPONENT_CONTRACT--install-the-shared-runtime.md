---
atom_family: SPEC
atom_id: AN-S-3297
container:
  component: C65
tier: 0
context:
  template: component_contract
  lens: DES
relations:
  ANSWERS:
  - AN-S-3296
state:
  status: draft
  version: 9
  updated_at: '2026-11-25T00:00:00+00:00'
---
## Summary

Install the shared runtime

## Guarantee

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
`INFO`. Validate and pass it to Studio at startup.

For a single Project, Release verifies Project access. Only explicit
`--init-project` initializes a new single Project.

`--agent codex` (or `--codex`) registers MCP and installs the user-scope `PreToolUse` hook. The hook selects the active Git worktree for each request. The user must trust the hook in Codex.

## Claim

### Prose Claim

`image_built` identifies an immutable shared runtime image.
`mcp_verified` requires a check through the published host port.

### Formal Claim

```python cli
declare_cli_contract(
    interface='runtime_setup',
    action='install_shared_runtime',
    runner='uv',
    path='LAYER_5_USER_SETUP_C65/setup.py',
    command='install',
    output='succeeded',
    must_effect=(('C27', 'image_built'), ('C27', 'runtime_started'), ('C27', 'mcp_verified')),
)
```
