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
  status: "archived"
  version: 1
  updated_at: "2026-11-22T10:58:40.674583+00:00"
---

## Summary

Install the shared runtime

## Guarantee

Run from a Framework checkout, with `<framework-checkout>` naming that checkout:

```sh
uv run --project <framework-checkout> --locked --python 3.14 --managed-python --no-env-file --group rmed-workflow-mcp python -B RUNTIME_SETUP/setup.py install [--project PATH | --projects-root PATH] [--settings PATH] [--port PORT] [--workbench-storage disk|memory] [--journal-storage files|duckdb] [--init-project --name NAME --prefix PREFIX] [--agent codex]
```

C65 imports no code from other Components. It calls C27 `build-image` through managed `uv`, and calls the C21 shared MCP launcher through managed `uv` and host Docker. It may call the Codex CLI when Codex is selected.

The `--codex` option is an alias for `--agent codex`. Before reporting success, C65 initializes the MCP session. For `--project`, it also calls the read-only `query_schema` tool for the selected Project.

C65 owns the schema and writes the machine-local `runtime.toml`. It writes repository input or initialization files only on explicit `--init-project`. It writes Codex user configuration only with `--agent codex` or its `--codex` alias.

## References

AN-S-3296@1 and AN-S-3288@5.
