---
atom_family: SPEC
atom_id: AN-S-3297
container:
  component: C65
tier: 1
context:
  template: component_contract
  lens: DES
state:
  status: "active"
  version: 4
  updated_at: '2026-11-22T12:51:19.669528+00:00'
---

## Summary

Install the shared runtime

## Guarantee

Run from the Framework checkout root.

```sh
setup="$PWD/LAYER_6_RUNTIME_SETUP"
UV_PROJECT_ENVIRONMENT="$setup/.venv-setup" \
  uv run --project "$PWD/LAYER_3_ENVIRONMENTS_C72/setup" \
    --locked --python 3.14 --managed-python --no-env-file \
    python -B -E "$setup/setup.py" install [--project PATH | --projects-root PATH] [--settings PATH] [--port PORT] [--workbench-storage disk|memory] [--journal-storage files|duckdb] [--init-project --name NAME --prefix PREFIX] [--agent codex]
```

C65 imports no code from other Components. It calls C27 `build-image` through managed `uv` in `release`. It calls the C21 shared MCP launcher through managed `uv` in `prod` and uses host Docker. It may call the Codex CLI when Codex is selected.

The `--codex` option is an alias for `--agent codex`. Before reporting success, C65 requests MCP verification through the C21 launcher. C21 opens the session from the host through the published port. For `--project`, C21 also calls the read-only `query_schema` tool for the selected Project.

C65 owns the schema and writes the machine-local `runtime.toml`. It writes repository input or initialization files only on explicit `--init-project`. It writes Codex user configuration only with `--agent codex` or its `--codex` alias.

## References

AN-S-3296, AN-S-3288@8, and AN-S-3310@6.
