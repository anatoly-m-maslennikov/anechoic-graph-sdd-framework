---
atom_family: SPEC
atom_id: AN-S-3587
container:
  component: C20
tier: 5
context:
  lens: DevOps
state:
  status: archived
  version: 14
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

encode explicit Docker runtime controls

## Claim

### Prose Claim

`docker/runtime.py` **must** carry explicit `build`, `start`, `stop`, `restart`, `status`, `logs` **and** `mcp` commands using the Project root **and** optional credential-file input.

## Details

### Scope

the Project-local Docker control adapter **and** existing MCP queue adapter.

- successful start writes `.anechoic_install/workflow_orchestrator/docker/transport.json`, selecting Docker queue routing for the existing MCP adapter.
- queue calls use fixed argument arrays **and** JSON stdin through `docker compose exec`; they do **not** interpolate shell text from requests.
- start/restart status distinguishes container existence, worker readiness **and** Agent readiness. no automatic restart policy is carried.
- stop retains the routing selection **and** persistent state, so an enqueue cannot silently target the native worker.
- `mcp` starts an interactive stdio client service **without** starting worker services. local service management does **not** create Run inputs.
- rebuilding the image **and** explicitly recreating services applies updated runtime code; MCP hot reload alone does **not** reload the worker image.

## Semantics

The retained AI-Agent service and its credentials are conditional on separately admitted AI-Agent execution. They do not require the current deterministic runtime to start or restore that service. The MCP and worker boundaries remain applicable to retained deterministic execution.
