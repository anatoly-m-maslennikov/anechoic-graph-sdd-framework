# Project-scoped Docker runtime

The image runs MCP services. It does not include an
AI Agent, Codex CLI, Agent credentials, mock Agent, or Agent service.

MCP receives the selected Project bind mount at `/project`.
The image and dependencies remain immutable at `/workspace`. HTTP MCP publishes
only on `127.0.0.1`; the stdio MCP service publishes no port. Startup does not
enqueue a Workflow or release anything.

## Build and run

```sh
UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine" --locked --no-sync --python 3.14 --managed-python --no-env-file \
  --group dev python -B \
  LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/runtime.py build

UV_PROJECT_ENVIRONMENT="$PWD/LAYER_4_ENGINE_STUDIO_C14/.venv-dev" PYTHONPATH="$PWD/LAYER_4_ENGINE_STUDIO_C14" uv run --no-compile-bytecode --project "$PWD/LAYER_3_DEVOPS_C80/LAYER_1_ENVIRONMENTS_C72/engine" --locked --no-sync --python 3.14 --managed-python --no-env-file \
  --group dev python -B \
  LAYER_4_ENGINE_STUDIO_C14/MCP_PATCHBAY_C21/FEATURE_MCP/docker/runtime.py mcp-http-start
```

`mcp-http-start` reports ready only after the loopback HTTP health check passes.

Images build with `ANECHOIC_RUNTIME_PROFILE=dev-preprod`. An explicit
Docker build can select another profile with
`--build-arg ANECHOIC_RUNTIME_PROFILE=prod`. To select a profile for a
container at startup, pass `-e ANECHOIC_RUNTIME_PROFILE=test` to `docker run`.
See [runtime profiles](../README.md#runtime-profiles) for the storage and
archive switches.

Shared Setup passes its configured Workbench and Journal storage values as
environment overrides. The same variables in the launch environment take
precedence over those settings.

`resources/DuckPGQ.LICENSE` was copied from `cwida/duckpgq-extension` at commit
`9c11bc192a071c9e44cef16cced90a22d7d7db2c`.

## MCP

Use `mcp` for stdio MCP and `mcp-http-start` for the Project HTTP endpoint.
The HTTP listener stays loopback-only. The MCP gateway and Workbench remain
independent of the retired AI Agent runtime.

## Persistent state

| State | Location |
| --- | --- |
| Workbench runtime | `.anechoic_runtime/workbench/` |

Historical Run data is retained outside this runtime.
