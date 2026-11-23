---
atom_family: SPEC
atom_id: AN-S-2432
container:
  component: C27
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 21
  updated_at: '2026-11-21T21:49:04.407565+00:00'
---

## Summary

provide isolated host execution for Release Runs

## Scope

the direct host invocation of Local or Public Release through `LAYER_5_FRAMEWORK_DELIVERY/release.py`.

## Claim

### Prose Claim

the Project host **must** execute Local and Public Release through the direct release entrypoint while preserving the separate authoring, host and Docker/MCP execution boundaries.

## Details

- the entrypoint validates the requested operation, Project root and Run ID before it invokes the corresponding Local or Public Release implementation.
- host-dependent release gates run in that direct host process. They do not require a Workflow Orchestrator Queue, worker, private IPC exchange or DBOS transport.
- the Docker/MCP runtime remains separately packaged and started by the release implementation; its process does not become the host release executor or receive the host's shared execution environment.
- an unavailable or invalid direct invocation stops and reports its actual result. No alternate executor is selected implicitly.
- release execution does not import or call ANECHOIC runtime Components or Journal.
- this capability does **not** authorize promotion, image deletion or replay of an uncertain effect. Those effects retain their existing gates.
